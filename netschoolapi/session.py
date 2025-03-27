import json
from dataclasses import dataclass
from http.cookiejar import CookieJar, Cookie
import time

from requests import session


class _CookiesPorter:
    def cookiejar_to_json(cookie_jar):
        cookies_list = []
        for cookie in cookie_jar:
            cookie_dict = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires,  # None если кука не имеет срока действия
                "secure": cookie.secure,
                "httponly": getattr(
                    cookie, "httponly", False
                ),  # Не всегда есть в Cookie,
                "comment": cookie.comment,
                "comment_url": cookie.comment_url,
                "rfc2109": cookie.rfc2109,
            }
            cookies_list.append(cookie_dict)

        return cookies_list

    def json_to_cookiejar(cookies_list):
        cookie_jar = CookieJar()

        for cookie_data in cookies_list:
            # Создаем объект Cookie из данных
            cookie = Cookie(
                version=0,  # Версия куки (обычно 0)
                name=cookie_data["name"],
                value=cookie_data["value"],
                port=None,
                port_specified=False,
                domain=cookie_data["domain"],
                domain_specified=True,
                domain_initial_dot=cookie_data["domain"].startswith("."),
                path=cookie_data["path"],
                path_specified=True,
                secure=cookie_data["secure"],
                expires=cookie_data["expires"],
                discard=False,
                comment=cookie_data.get("comment"),
                comment_url=cookie_data.get("comment_url"),
                rest=cookie_data.get("rest", {}),
                rfc2109=cookie_data["rfc2109"],
            )
            cookie_jar.set_cookie(cookie)
        return cookie_jar


@dataclass
class Session:
    cookiejar: CookieJar
    access_token: str
    access_token_sent: float
    access_token_expires: float
    is_saved: bool = False

    def is_access_token_expired(self) -> bool:
        cur_time = time.time()
        return self.access_token_expires < cur_time

    def to_json(self) -> str:
        session_data = self.__dict__.copy()
        session_data["cookiejar"] = _CookiesPorter.cookiejar_to_json(
            session_data["cookiejar"]
        )
        return session_data

    @classmethod
    def from_json(cls, path: str) -> "Session":
        with open(path, "r") as f:
            session_data: dict = json.loads(f.read())
        cookiejar = _CookiesPorter.json_to_cookiejar(session_data["cookiejar"])
        session_data["cookiejar"] = cookiejar
        return cls(**session_data)
