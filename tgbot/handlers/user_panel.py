import logging
import re

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, PreCheckoutQuery
from aiogram.utils.chat_action import ChatActionSender

from tgbot.create_bot import bot, db, PAYMENT_PROVIDER_TOKEN
from tgbot.handlers.payment_handler import process_pre_checkout_query, process_successful_payment, PRICE
from tgbot.keyboards.manage_kb import home_page_kb, main_kb

user_router = Router()
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    waiting_for_product_link = State()
    waiting_for_payment = State()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        pass

@user_router.message(F.text.contains('О нас'))
async def get_chanel_statistics(message: Message):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        pass

@user_router.message(F.text.contains('Назад'))
async def handle_back(message: Message, state: FSMContext):
    pass

@user_router.message(F.text == '📝 Опубликовать товар')
async def publish_product(message: Message, state: FSMContext):
    pass
@user_router.message(F.text, Form.waiting_for_product_link)
async def process_product_link(message: Message, state: FSMContext):
    pass
@user_router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    pass

@user_router.message()
async def handle_successful_payment(message: Message, state: FSMContext):
    pass