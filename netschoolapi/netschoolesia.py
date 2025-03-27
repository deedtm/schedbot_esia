import httpx
import os

from datetime import date, timedelta
from httpx import Cookies
from io import BytesIO
from typing import Optional, Dict, List, Callable, Coroutine

from . import errors, schemas
from .async_client_wrapper import Requester
from .netschoolapi import NetSchoolAPI
from .selenium_netschool import SeleniumNetSchool
from .session import Session


class NetSchoolESIA(NetSchoolAPI):
    def __init__(
        self,
        url: str,
        esia_captcha_handler: Optional[Callable | Coroutine] = None,
        esia_suspicious_activity_handler: Optional[Callable | Coroutine] = None,
        default_requests_timeout: int = None,
    ):
        super().__init__(url, default_requests_timeout)
        self.selenium_ns = SeleniumNetSchool(
            url, esia_captcha_handler, esia_suspicious_activity_handler
        )
        self.sessions: dict[str, Session] = {}
        self.sessions_directory = os.path.join(os.path.dirname(__file__), "sessions")

    async def login_by_session(
        self,
        session_id: str,
        session: Session = None,
        requests_timeout: int = None,
    ):
        assert self.sessions.get(session_id) is not None or session is not None, "No session provided"
        
        current_session = self.sessions.get(session_id)
        current_session_expired = not session and current_session and current_session.is_access_token_expired()
        if current_session_expired:
            raise errors.AuthError("Current session access token is expired. Please provide session or login by esia")

        new_session_expired = not current_session and session and not session.is_access_token_expired()
        if new_session_expired:
            raise errors.AuthError("Given session access token is expired. Please login by esia")
        
        if self.sessions.get(session_id) is None:
            self.sessions.setdefault(session_id, session)
            
        await NetSchoolESIA.login(self, session_id, requests_timeout)

    async def login_by_esia(
        self,
        session_id: str,
        esia_login: str,
        esia_password: str,
        requests_timeout: int = None,
    ):
        saved_session = self.sessions.get(session_id)
        if saved_session is None or saved_session.is_access_token_expired():
            cookiejar, access_token_data = await self.selenium_ns.get_session_data(
                esia_login, esia_password
            )
            self._login_data = (esia_login, esia_password)
            self.sessions.setdefault(session_id, Session(cookiejar, **access_token_data))
            
        await NetSchoolESIA.login(self, session_id, requests_timeout)

    async def login(self, session_id: str, requests_timeout: int = None):
        requester = self._wrapped_client.make_requester(requests_timeout)
        
        session = self.sessions.get(session_id)
        self._wrapped_client.client._cookies = Cookies(session.cookiejar)
        self._wrapped_client.client.headers["at"] = session.access_token

        response = await requester(
            self._wrapped_client.client.build_request(
                method="GET",
                url="student/diary/init",
            )
        )
        diary_info = response.json()
        student = diary_info["students"][diary_info["currentStudentId"]]
        self._student_id = student["studentId"]

        response = await requester(
            self._wrapped_client.client.build_request(method="GET", url="years/current")
        )
        year_reference = response.json()
        self._year_id = year_reference["id"]

        response = await requester(
            self._wrapped_client.client.build_request(
                method="GET",
                url="grade/assignment/types",
                params={"all": False},
            )
        )
        assignment_reference = response.json()
        self._assignment_types = {
            assignment["id"]: assignment["name"] for assignment in assignment_reference
        }

    async def _request_with_optional_relogin(
        self,
        requests_timeout: Optional[int],
        request: httpx.Request,
        follow_redirects=False,
    ):
        try:
            response = await self._wrapped_client.request(
                requests_timeout, request, follow_redirects
            )
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.UNAUTHORIZED:
                if self._login_data:
                    await self.login(*self._login_data)
                    return await self._request_with_optional_relogin(
                        requests_timeout, request, follow_redirects
                    )
                else:
                    raise errors.AuthError(
                        ".login() before making requests that need " "authorization"
                    )
            else:
                raise http_status_error
        else:
            return response

    # async def download_attachment(
    #     self, attachment_id: int, buffer: BytesIO, requests_timeout: int = None
    # ):
    #     buffer.write(
    #         (
    #             await self._request_with_optional_relogin(
    #                 requests_timeout,
    #                 self._wrapped_client.client.build_request(
    #                     method="GET",
    #                     url=f"attachments/{attachment_id}",
    #                 ),
    #             )
    #         ).content
    #     )

    async def diary(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        requests_timeout: int = None,
    ) -> schemas.Diary:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="student/diary",
                params={
                    "studentId": self._student_id,
                    "yearId": self._year_id,
                    "weekStart": start.isoformat(),
                    "weekEnd": end.isoformat(),
                },
            ),
        )
        diary_schema = schemas.DiarySchema()
        diary_schema.context["assignment_types"] = self._assignment_types
        diary = diary_schema.load(response.json())
        return diary  # type: ignore

    async def overdue(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        requests_timeout: int = None,
    ) -> List[schemas.Assignment]:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="student/diary/pastMandatory",
                params={
                    "studentId": self._student_id,
                    "yearId": self._year_id,
                    "weekStart": start.isoformat(),
                    "weekEnd": end.isoformat(),
                },
            ),
        )
        assignments_schema = schemas.AssignmentSchema()
        assignments_schema.context["assignment_types"] = self._assignment_types
        assignments = assignments_schema.load(response.json(), many=True)
        return assignments  # type: ignore

    async def announcements(
        self, take: Optional[int] = -1, requests_timeout: int = None
    ) -> List[schemas.Announcement]:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="announcements",
                params={"take": take},
            ),
        )
        announcements = schemas.AnnouncementSchema().load(response.json(), many=True)
        return announcements  # type: ignore

    async def attachments(
        self, assignment_id: int, requests_timeout: int = None
    ) -> List[schemas.Attachment]:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="POST",
                url="student/diary/get-attachments",
                params={"studentId": self._student_id},
                json={"assignId": [assignment_id]},
            ),
        )
        response = response.json()
        if not response:
            return []
        attachments_json = response[0]["attachments"]
        attachments = schemas.AttachmentSchema().load(attachments_json, many=True)
        return attachments  # type: ignore

    async def school(self, requests_timeout: int = None) -> schemas.School:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="schools/{0}/card".format(self._school_id),
            ),
        )
        school = schemas.SchoolSchema().load(response.json())
        return school  # type: ignore

    async def logout(self, requests_timeout: int = None):
        try:
            await self._wrapped_client.request(
                requests_timeout,
                self._wrapped_client.client.build_request(
                    method="POST",
                    url="auth/logout",
                ),
            )
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.UNAUTHORIZED:
                # Session is dead => we are logged out already
                # OR
                # We are logged out already
                pass
            else:
                raise http_status_error

    async def full_logout(self, requests_timeout: int = None):
        await self.logout(requests_timeout)
        await self._wrapped_client.client.aclose()

    async def schools(self, requests_timeout: int = None) -> List[schemas.ShortSchool]:
        resp = await self._wrapped_client.request(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="schools/search?name=У",
            ),
        )
        schools = schemas.ShortSchoolSchema().load(resp.json(), many=True)
        return schools  # type: ignore

    async def _get_school_id(
        self, school_name: str, requester: Requester
    ) -> Dict[str, int]:
        schools = (
            await requester(
                self._wrapped_client.client.build_request(
                    method="GET",
                    url=f"schools/search?name={school_name}",
                )
            )
        ).json()

        for school in schools:
            if school["shortName"] == school_name:
                self._school_id = school["id"]
                return school["id"]
        raise errors.SchoolNotFoundError(school_name)

    async def download_profile_picture(
        self, user_id: int, buffer: BytesIO, requests_timeout: int = None
    ):
        buffer.write(
            (
                await self._request_with_optional_relogin(
                    requests_timeout,
                    self._wrapped_client.client.build_request(
                        method="GET",
                        url="users/photo",
                        params={"at": self.session.access_token, "userId": user_id},
                    ),
                    follow_redirects=True,
                )
            ).content
        )
