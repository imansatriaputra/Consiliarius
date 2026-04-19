import logging
import os
from typing import TYPE_CHECKING

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot

from mansa import generate_morning_briefing, generate_weekly_review
from memory.memory_manager import MemoryManager

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)
WIB = pytz.timezone("Asia/Jakarta")


async def send_morning_briefing(bot: Bot, chat_id: str, memory: MemoryManager):
    try:
        briefing = await generate_morning_briefing(memory)
        await bot.send_message(chat_id=chat_id, text=briefing)
        logger.info("Morning briefing sent.")
    except Exception as e:
        logger.error(f"Morning briefing failed: {e}")


async def send_weekly_review(bot: Bot, chat_id: str, memory: MemoryManager):
    try:
        review = await generate_weekly_review(memory)
        await bot.send_message(chat_id=chat_id, text=review)
        logger.info("Weekly review sent.")
    except Exception as e:
        logger.error(f"Weekly review failed: {e}")


def setup_scheduler(bot: Bot, chat_id: str, memory: MemoryManager) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=WIB)

    scheduler.add_job(
        send_morning_briefing,
        trigger="cron",
        hour=7,
        minute=0,
        args=[bot, chat_id, memory],
        id="morning_briefing",
        name="MANSA Morning Briefing",
        replace_existing=True,
    )

    scheduler.add_job(
        send_weekly_review,
        trigger="cron",
        day_of_week="sun",
        hour=8,
        minute=0,
        args=[bot, chat_id, memory],
        id="weekly_review",
        name="MANSA Weekly Review",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started — morning briefing at 07:00 WIB, weekly review Sundays 08:00 WIB.")
    return scheduler
