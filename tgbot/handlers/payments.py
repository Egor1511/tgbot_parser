import logging

import requests
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message

from tgbot.create_bot import PAYMENT_PROVIDER_TOKEN
from tgbot.keyboards.manage_kb import main_kb
from tgbot.parser.wb_parser import WBParser

PRICE = LabeledPrice(label="Публикация товара",
                     amount=x)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def process_pre_checkout_query(pre_checkout_q: PreCheckoutQuery,
                                     bot: Bot):
    pass

async def process_successful_payment(message: Message, state: FSMContext, db):
    pass

async def refund_payment(payment_id: str, amount: str):
    pass
