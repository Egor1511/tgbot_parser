import asyncio
import logging

from create_bot import bot, dp, scheduler
from tgbot.handlers.user_router import user_router
from tgbot.handlers.admin_panel import admin_router, post_product


async def main():
    logging.basicConfig(level=logging.INFO)
    scheduler.start()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(),
                           skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())