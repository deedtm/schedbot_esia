import asyncio
import random
import nodriver as uc
from http.cookiejar import CookieJar
from typing import Callable, Optional, Coroutine
from time import time

from . import logger as l
from .errors import AuthError, AuthFailException
from .constants import MAX_SESSION_IDLE_TIME

def default_captcha_handler(filename: str):
    return input(f"Enter code from {filename} or enter 'new' to get new code: ")


def default_suspicious_activity_handler(reason: str):
    return input(reason + ": ")


class SeleniumNetSchool:
    def __init__(
        self,
        netschool_url: str,
        esia_captcha_handler: Optional[Callable | Coroutine] = None,
        esia_suspicious_activity_handler: Optional[Callable | Coroutine] = None,
    ):
        self.netschool_url = netschool_url
        self.captcha_handler = (
            default_captcha_handler
            if esia_captcha_handler is None
            else esia_captcha_handler
        )
        self.susactivity_handler = (
            default_suspicious_activity_handler
            if esia_suspicious_activity_handler is None
            else esia_suspicious_activity_handler
        )
        self.access_token = None
        self.browser = None
        self.login_data = None
        self.handler_urls = []

    async def __sleep(self, page, additional_time: int = 0):
        await page
        sleep_time = random.uniform(0.5, 1) + additional_time
        await asyncio.sleep(sleep_time)

    async def __send_keys(self, text: str, element: uc.Element):
        timings = [random.random() / 10 for _ in text]
        # print(f"{timings=}")
        for ind, t in enumerate(timings):
            await element.send_keys(text[ind])
            await asyncio.sleep(t)

    async def __get_to_esia_page(self, page: uc.Tab, try_: int = 1):
        l.debug(f'Try #{try_} to get to ESIA page')
        try:
            if try_ > 1:
                await self.__sleep(page, 5 * (1 + try_ / 5))
            return await page.select("#login.plain-input"), page
        except NameError as e:
            if try_ > 8:
                l.debug("Couldn't get to esia page")
                raise AuthFailException("Couldn't get to esia page")
            if try_ % 2 == 0:
                self.browser.stop()
                self.browser = await uc.start()
                page = await self.browser.get()
                l.debug("Started new browser instance")
            page = await page.get(self.netschool_url)
            page = await self.__goto_esia_login()
            return await self.__get_to_esia_page(page, try_ + 1)

    async def __captcha_save_img(self, page: uc.Tab):
        captcha_img = await page.select("img.esia-captcha__image")
        filename = f"captcha_{time()}.jpg"
        await captcha_img.save_screenshot(filename)
        return filename

    async def __captcha_solve(self, page: uc.Tab, code: str):
        captcha_input = await page.select("input.code-entry__input")
        await captcha_input.focus()
        await self.__send_keys(code, captcha_input)
        await self.__sleep(page)
        captcha_button = await page.select("button.code-entry__button")
        await captcha_button.click()

    async def __renew_captcha(self, page: uc.Tab):
        new_button = await page.select(
            "button.esia-captcha__button.esia-captcha__button_renew"
        )
        await new_button.focus()
        await new_button.click()
        await self.__sleep(page)

        try:
            await page.select("h3.captcha-error__title")
            await page.reload()
            await self.__login_esia(page, *self.login_data, True)
        except NameError:
            pass
        captcha_filename = await self.__captcha_save_img(page)
        return captcha_filename

    async def __captcha_handler(self, page: uc.Tab, in_recursion: bool = False):
        if in_recursion:
            return
        try:
            captcha_filename = await self.__captcha_save_img(page)
            code = "new"
            while code == "new":
                if asyncio.iscoroutinefunction(self.captcha_handler):
                    code = await self.captcha_handler(captcha_filename)
                else:
                    code = self.captcha_handler(captcha_filename)
                if code == "new":
                    captcha_filename = await self.__renew_captcha(page)
            await self.__captcha_solve(page, code)
        except NameError:
            pass

    async def __susactivity_get_reason(self, page: uc.Tab):
        suspicious_activity = await page.select(
            "h3.anomaly__title-h3.abstract-request-information__title"
        )
        print(suspicious_activity.text.strip())
        confirmation_reqs = await page.select(
            "p.anomaly__plain-text.abstract-request-information__text"
        )
        return confirmation_reqs.text.strip()

    async def __susactivity_solve(self, page: uc.Tab, code: str):
        confirmation_input = await page.select("input.input__field")
        await self.__send_keys(code, confirmation_input)
        await self.__sleep(page)
        confirmation_button = await page.select("button.input__button.anomaly__button")
        await confirmation_button.click()
        await self.__sleep(page)

    async def __susactivity_handler(self, page: uc.Tab):
        try:
            reason = await self.__susactivity_get_reason(page)
            if asyncio.iscoroutinefunction(self.susactivity_handler):
                code = await self.susactivity_handler(reason)
            else:
                code = self.susactivity_handler(reason)
            await self.__susactivity_solve(page, code)
        except NameError:
            pass

    async def __goto_esia_login(self):
        page = await self.browser.get(self.netschool_url, new_tab=True)
        esia_button = await page.find("Вход для учащихся")
        await esia_button.focus()
        await esia_button.click()
        await self.__sleep(page, 5)
        return page

    async def __login_esia(
        self, page: uc.Tab, login: str, password: str, in_recursion: bool = False
    ):
        login_input, page = await self.__get_to_esia_page(page)
        await login_input.focus()
        await self.__send_keys(login, login_input)
        await self.__sleep(page)

        pwd_input = await page.select("#password.plain-input")
        await pwd_input.focus()
        await self.__send_keys(password, pwd_input)
        await self.__sleep(page)

        esia_login_button = await page.find("Войти")
        await esia_login_button.focus()
        await esia_login_button.click()
        await self.__sleep(page)

        try:
            error = await page.select("div.error-label")
            self.browser.stop()
            raise AuthError(error.text)
        except NameError:
            pass
        self.login_data = (login, password)
        await self.__captcha_handler(page, in_recursion)
        await self.__susactivity_handler(page)
        return page

    async def __login_sgo_esia(self, login: str, password: str):
        page = await self.__goto_esia_login()
        page = await self.__login_esia(page, login, password)
        return page

    async def __response_handler(self, e: uc.cdp.network.ResponseReceived):
        url = e.response.url
        self.handler_urls.append(url)
        if "/webapi/settings?at=" in url:
            sent_epoch = e.response.response_time / 1000
            expires_in = sent_epoch + MAX_SESSION_IDLE_TIME
            self.at_data = {
                "access_token": url.split("=")[1].split("&")[0],
                "access_token_sent": sent_epoch,
                "access_token_expires": expires_in,
            }
            self.page.handlers.clear()

    async def get_session_data(self, login: str, password: str):
        if self.browser is None or self.browser.stopped:
            self.browser = await uc.start(sandbox=False, browser_args=['--headless=new'])
        try:
            l.info('Logging in to SGO by ESIA...')
            page: uc.Tab = await self.__login_sgo_esia(login, password)

            self.handler_urls = []
            page.add_handler(uc.cdp.network.ResponseReceived, self.__response_handler)
            self.page = page
            await page.reload()
            await self.__sleep(page, 8)
            cookies = await self.browser.cookies.get_all(True)
            self.browser.stop()

            jar = CookieJar()
            for c in cookies:
                jar.set_cookie(c)

            return jar, self.at_data
        finally:
            if self.browser is not None:
                self.browser.stop()
            self.browser = None

    