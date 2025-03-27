from typing import Any, Awaitable, Callable, Dict
from random import choice

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramRetryAfter
from aiogram.fsm.context import FSMContext

from ..constants import ERRS, COMMANDS, CLOCK_EMOJI

from database.exceptions import MissingCredentials
from netschool.errors import LoginError
from netschoolapi.errors import AuthError, NoResponseFromServer


class GeneralMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        update: Message | CallbackQuery,
        data: Dict[str, Any],
    ):
        msg = update if isinstance(update, Message) else update.message
        is_callback = isinstance(update, CallbackQuery)

        if not is_callback:
            template = COMMANDS['waiting']
            text = template.format(emoji=choice(CLOCK_EMOJI))
            wait_msg = await update.answer(text)
            params = data['handler'].params
            wait_param_names = ['wait_message', 'wait_msg', 'wmsg']
            for param_name in wait_param_names:
                if param_name in params:
                    data[param_name] = wait_msg
                    break
        # else:
        #     template = COMMANDS['callback_waiting']
        # двойной callback.answer() не поддерживается(((((   
        
        try: 
            return await handler(update, data)
        except NoResponseFromServer:
            text = ERRS["no_response_from_server"]
            if is_callback:
                await update.answer(text=text, show_alert=True)
            else:
                await wait_msg.edit_text(text=text)
        except AuthError:
            await wait_msg.edit_text(text=ERRS["wrong_credentials"])
        except LoginError:
            await wait_msg.edit_text(text=ERRS["login_error"])
        except MissingCredentials:
            await wait_msg.edit_text(text=ERRS["credentials_are_missing"])
        except TelegramRetryAfter as err:
            seconds = err.__str__().split("(")[0].split()[-1]
            await msg.answer(text=ERRS["retry_after"].format(seconds=seconds))
