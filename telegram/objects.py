from aiogram import Router

from netschool import NSWrapper

from .kb import Keyboards
from .middlewares import *
from config.netschool import NETSCHOOL_URL

router = Router()
router.message.middleware(DatabaseMissingInMiddleware())
router.my_chat_member.middleware(DatabaseMissingInMiddleware())

router.message.middleware(DatabaseTableMiddleware())
router.callback_query.middleware(DatabaseTableMiddleware())
router.my_chat_member.middleware(DatabaseTableMiddleware())

router.message.middleware(GeneralMiddleware())
router.callback_query.middleware(GeneralMiddleware())

kb = Keyboards()
ns = NSWrapper(NETSCHOOL_URL)
