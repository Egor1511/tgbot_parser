import asyncio
import logging

from aiogram import Router, F
from aiogram.client.session import aiohttp
from aiogram.types import Message
from apscheduler.triggers.interval import IntervalTrigger

from tgbot.create_bot import bot, db, admins, CHAT, scheduler
from tgbot.keyboards.manage_kb import accept_or_reject, main_kb, \
    manage_flow_kb, home_page_kb
from tgbot.parser.main import main_parsing
from tgbot.utils.utils import format_product_text

admin_router = Router()
logger = logging.getLogger(__name__)


async def handle_product_action(message: Message, action: str):
    """Handles product actions for acceptance or rejection."""
    pass

@admin_router.message((F.text == '') & (
        F.from_user.id.in_(admins)))
async def show_suggested_products(message: Message):
    """Shows suggested products for admin approval."""
    pass

@admin_router.message((F.text == '') & (F.from_user.id.in_(admins)))
async def accept_product(message: Message):
    """Accepts the suggested product."""
    pass

@admin_router.message((F.text == '') & (F.from_user.id.in_(admins)))
async def reject_product(message: Message):
    """Rejects the suggested product."""
    pass

@admin_router.message(F.text == '')
async def manage_flow(message: Message):
    pass
@admin_router.message(F.text == '')
async def manage_flow(message: Message):
    pass
@admin_router.message(F.text == '')
async def stop_flow(message: Message):
    pass
@admin_router.message(F.text == '')
async def resume_flow(message: Message):
    pass
@admin_router.message(F.text == '')
async def change_flow_speed(message: Message):
    pass
@admin_router.message(F.text.regexp(r''))
async def set_flow_speed(message: Message):
    pass
@admin_router.message(F.text == '')
async def update_flow(message: Message):
    pass
@admin_router.message(F.text == '')
async def get_real_cards_count(message: Message):
    pass