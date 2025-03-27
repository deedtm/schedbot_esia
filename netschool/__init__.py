import logging as l
import os
from datetime import date
from io import BytesIO

import httpx

from netschoolapi import NetSchoolESIA
from netschoolapi.errors import NoResponseFromServer
from netschoolapi.schemas import Assignment, Attachment
from netschoolapi.session import Session

from .errors import LoginError, MissingCredentials
from .sessions import NSSession


__all__ = ["NSWrapper"]


class NSWrapper(NetSchoolESIA):
    def __init__(
        self,
        url,
        esia_captcha_handler=None,
        esia_suspicious_activity_handler=None,
        default_requests_timeout=None,
    ):
        self.url = url
        self.sessions: dict[str, Session] = {}
        self.nssession = NSSession(os.path.join(os.path.dirname(__file__), "sessions"))
        self.log = l.getLogger(__name__)

        super().__init__(
            url,
            esia_captcha_handler,
            esia_suspicious_activity_handler,
            default_requests_timeout,
        )

    async def _wrapper_login(
        self, chat_id: int, *, login: str = None, password: str = None
    ):
        session_id = str(chat_id)
        session = self.sessions.get(session_id)
        assert (
            session or login and password
        ), "You must provide login and password if session is None"

        if session is None:
            login_func = self.login_by_esia(session_id, login, password)
        else:
            login_func = self.login_by_session(session_id, session)

        _try = 0
        while _try < 5:
            lf = login_func
            self.log.debug(f"{chat_id}:Try to login #{_try}")
            try:
                await lf
                self.log.debug(f"{chat_id}:Success login")
                break
            except NoResponseFromServer:
                _try += 1
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    login_func = self.login_by_esia(session_id, login, password)
                else:
                    _try += 1
                    raise e
            except Exception as e:
                raise e
        else:
            raise LoginError()

    async def login(self, chat_id: int, login: str, password: str):
        session_id = str(chat_id)
        cur_session = self.sessions.get(session_id)
        found_session = self.nssession.get(chat_id)

        valid_cur_session = cur_session and not cur_session.is_access_token_expired()
        valid_found_session = (
            found_session and not found_session.is_access_token_expired()
        )

        if found_session:
            self.log.debug(f"{session_id}:Found session. Valid: {valid_found_session}")

        kwargs = {}
        if valid_cur_session:
            self.log.debug(f"{session_id}:Current session is valid")
        elif valid_found_session:
            self.log.debug(
                f"{session_id}:Current session is invalid. Using found session"
            )
            self.sessions.setdefault(session_id, found_session)
        else:
            self.log.debug(
                f"{session_id}:No valid sessions found. Using login and password"
            )
            kwargs.update(login=login, password=password)

        await self._wrapper_login(chat_id, **kwargs)
            
    async def logout(self, chat_id: int):
        session_id = str(chat_id)
        session = self.sessions.get(session_id)
        valid_session = session and not session.is_access_token_expired()
        if valid_session or session.is_saved:
            session.is_saved = True
            self.nssession.save(chat_id, session)
            self.log.debug(f"{session_id}:Session saved")
        elif valid_session and session.is_saved:
            pass
        else:
            self.sessions.pop(session_id, None)
            await NetSchoolESIA.logout(self, chat_id)
            self.log.debug(f"{session_id}:Logged out")

    async def get_diary(self, start: date = None, end: date = None):
        return await self.diary(start, end)

    async def get_attachments(self, assignment: Assignment):
        return await self.attachments(assignment.id)

    async def pics_generator(self, attachments: list[Attachment]):
        buffer = BytesIO()
        for attachment in attachments:
            await self.download_attachment(attachment.id, buffer)
            yield buffer.getvalue(), attachment.name
