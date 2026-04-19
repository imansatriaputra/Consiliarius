import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import Application

load_dotenv()

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logger = logging.getLogger("mansa")


def validate_env():
    required = ["TELEGRAM_BOT_TOKEN", "ANTHROPIC_API_KEY"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    optional_warn = {
        "GROQ_API_KEY": "voice transcription (Groq Whisper) disabled",
        "ELEVENLABS_API_KEY": "voice responses (ElevenLabs) disabled",
        "ELEVENLABS_VOICE_ID": "voice responses (ElevenLabs) disabled",
        "TELEGRAM_CHAT_ID": "bot open to anyone — set this to restrict access",
    }
    for var, msg in optional_warn.items():
        if not os.getenv(var):
            logger.warning(f"{var} not set — {msg}")


async def post_init(app: Application):
    from memory.memory_manager import MemoryManager
    from scheduler import setup_scheduler

    memory: MemoryManager = app.bot_data["memory"]
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if chat_id:
        setup_scheduler(app.bot, chat_id, memory)
        logger.info(f"Scheduler running for chat_id {chat_id}")
    else:
        logger.warning("TELEGRAM_CHAT_ID not set — scheduler disabled")

    logger.info("MANSA is online.")


def main():
    validate_env()

    from bot import setup_handlers
    from memory.memory_manager import MemoryManager

    memory = MemoryManager()

    app = (
        Application.builder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .post_init(post_init)
        .build()
    )

    app.bot_data["memory"] = memory
    setup_handlers(app, memory)

    logger.info("Starting MANSA...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
