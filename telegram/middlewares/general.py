from typing import Any, Awaitable, Callable, Dict
from random import choice

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramRetryAfter

from ..constants import ERRS, COMMANDS, CLOCK_EMOJI

from database.exceptions import MissingCredentials
from netschool.errors import LoginError
from netschoolapi.errors import AuthError, AuthFailException, NoResponseFromServer
from time import time


class GeneralMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        update: Message | CallbackQuery,
        data: Dict[str, Any],
    ):
        
        is_message = isinstance(update, Message)
        is_callback = isinstance(update, CallbackQuery)

        msg = update if is_message else update.message

        is_private = msg.chat.type == "private"


        # Flood control and temporary blocks
        if not hasattr(GeneralMiddleware, '_active_requests'):
            GeneralMiddleware._active_requests = {}
        if not hasattr(GeneralMiddleware, '_violation_counts'):
            GeneralMiddleware._violation_counts = {}
        if not hasattr(GeneralMiddleware, '_blocked_until'):
            GeneralMiddleware._blocked_until = {}

        user_id = update.from_user.id
        current_time = time()

        # Check if user is currently blocked
        is_user_blocked = user_id in GeneralMiddleware._blocked_until and current_time < GeneralMiddleware._blocked_until[user_id]

        if is_user_blocked:
            block_time_left = int(GeneralMiddleware._blocked_until[user_id] - current_time)
            block_template = ERRS.get("user_blocked", "You are temporarily blocked for {block_time_left} seconds due to flood control violation.")
            block_msg = block_template.format(block_time_left=block_time_left)
            if is_callback:
                await update.answer(text=block_msg, show_alert=True)
            elif is_private:
                await update.answer(text=block_msg)

        # Check if the user already has an active request
        if user_id in GeneralMiddleware._active_requests and GeneralMiddleware._active_requests[user_id]:
            # Increment violation count
            GeneralMiddleware._violation_counts[user_id] = GeneralMiddleware._violation_counts.get(user_id, 0) + 1
            
            # Calculate block duration (increases with violations)
            violation_count = GeneralMiddleware._violation_counts[user_id]
            block_duration = min(300, 10 * (2 ** (violation_count - 1)))  # 10, 20, 40, 80, 160, 300 seconds
            
            # Block the user
            GeneralMiddleware._blocked_until[user_id] = current_time + block_duration
            
            flood_msg = ERRS.get("flood_control", f"Please wait for your previous request to complete. You are now blocked for {block_duration} seconds.")
            if is_callback:
                await update.answer(text=flood_msg, show_alert=True)
            elif is_private:
                await update.answer(text=flood_msg)
            return

        # Reset violation count if user is behaving properly
        if user_id in GeneralMiddleware._violation_counts and GeneralMiddleware._violation_counts[user_id] > 0:
            GeneralMiddleware._violation_counts[user_id] = max(0, GeneralMiddleware._violation_counts[user_id] - 1)

        # Mark user as having an active request
        GeneralMiddleware._active_requests[user_id] = True

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
        
        err_text = None
        
        try:
            if not is_user_blocked:
                return await handler(update, data)
        except NoResponseFromServer:
            err_text = ERRS["no_response_from_server"]
        except AuthFailException:
            err_text = ERRS['auth_failed']
        except AuthError:
            err_text = ERRS['wrong_credentials']
        except LoginError:
            err_text = ERRS['login_error']
        except MissingCredentials:
            err_text = ERRS['credentials_are_missing']
        except TelegramRetryAfter as err:
            seconds = err.__str__().split("(")[0].split()[-1]
            await msg.answer(text=ERRS["retry_after"].format(seconds=seconds))
            return
        finally:
            if err_text is not None:
                if is_callback:
                    await update.answer(text=err_text, show_alert=True)
                else:
                    wait_msg.edit_text(text=err_text)
            # Mark user's request as complete
            if user_id in GeneralMiddleware._active_requests:
                GeneralMiddleware._active_requests[user_id] = False
            