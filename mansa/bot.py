import io
import logging
import os
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from mansa import process_message
from memory.memory_manager import MemoryManager
from voice import generate_voice_response, is_elevenlabs_available, is_groq_available, transcribe_voice
from vision import analyze_image, analyze_video, is_opencv_available

logger = logging.getLogger(__name__)

_memory: MemoryManager = None


def get_memory() -> MemoryManager:
    global _memory
    if _memory is None:
        _memory = MemoryManager()
    return _memory


def is_authorized(update: Update) -> bool:
    authorized_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not authorized_id:
        return True
    return str(update.effective_chat.id) == authorized_id.strip()


async def _send_response(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    chat_id = update.effective_chat.id
    memory = get_memory()

    await update.message.reply_text(text)

    if is_elevenlabs_available() and len(text) <= 1000:
        try:
            voice_bytes = await generate_voice_response(text)
            if voice_bytes:
                audio_file = io.BytesIO(voice_bytes)
                audio_file.name = "mansa.mp3"
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_file,
                    title="MANSA",
                    filename="mansa.mp3",
                )
        except Exception:
            pass


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text("Back online. Ready when you are, Iman.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    chat_id = str(update.effective_chat.id)
    memory = get_memory()
    user_text = update.message.text

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    response = await process_message(user_text, chat_id, memory)
    await _send_response(update, context, response)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    chat_id = str(update.effective_chat.id)
    memory = get_memory()

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if not is_groq_available():
        response = await process_message(
            "[Voice note received — Groq API key not configured, transcription unavailable]",
            chat_id,
            memory,
        )
        await _send_response(update, context, response)
        return

    voice = update.message.voice
    tg_file = await voice.get_file()

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await tg_file.download_to_drive(tmp_path)
        transcription = await transcribe_voice(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not transcription:
        await update.message.reply_text("Didn't catch that. Try again.")
        return

    memory.add_memory_entry(
        content=f"Voice note: {transcription}",
        keywords=["voice", "audio"] + transcription.split()[:5],
        entry_type="voice",
    )

    response = await process_message(transcription, chat_id, memory)
    await _send_response(update, context, response)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    chat_id = str(update.effective_chat.id)
    memory = get_memory()
    caption = update.message.caption or ""

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    photo = update.message.photo[-1]
    tg_file = await photo.get_file()

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await tg_file.download_to_drive(tmp_path)
        analysis = await analyze_image(tmp_path, user_context=caption)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    memory.add_memory_entry(
        content=f"Image analysis — {caption or 'no caption'}: {analysis[:300]}",
        keywords=["image", "visual", "photo"] + (caption.lower().split()[:5] if caption else []),
        entry_type="image",
        extra={"user_context": caption},
    )

    full_message = f"{caption}\n\n{analysis}" if caption else analysis
    response = await process_message(full_message, chat_id, memory)
    await _send_response(update, context, response)


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    chat_id = str(update.effective_chat.id)
    memory = get_memory()
    caption = update.message.caption or ""

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if not is_opencv_available():
        await update.message.reply_text(
            "Video processing requires opencv-python-headless. "
            "It's not installed in this environment — send individual frames instead."
        )
        return

    video = update.message.video
    tg_file = await video.get_file()

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await tg_file.download_to_drive(tmp_path)
        analysis = await analyze_video(tmp_path, user_context=caption)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    memory.add_memory_entry(
        content=f"Video analysis — {caption or 'no caption'}: {analysis[:300]}",
        keywords=["video", "visual"] + (caption.lower().split()[:5] if caption else []),
        entry_type="video",
        extra={"user_context": caption},
    )

    full_message = f"{caption}\n\n{analysis}" if caption else analysis
    response = await process_message(full_message, chat_id, memory)
    await _send_response(update, context, response)


async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    chat_id = str(update.effective_chat.id)
    memory = get_memory()
    memory.clear_conversation(chat_id)
    await update.message.reply_text("Conversation cleared. Memory is intact.")


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    groq = "✓" if is_groq_available() else "✗"
    eleven = "✓" if is_elevenlabs_available() else "✗"
    opencv = "✓" if is_opencv_available() else "✗"

    status = (
        f"MANSA — system status\n\n"
        f"Claude API: ✓\n"
        f"Groq (voice in): {groq}\n"
        f"ElevenLabs (voice out): {eleven}\n"
        f"OpenCV (video): {opencv}"
    )
    await update.message.reply_text(status)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Unhandled error: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Something went wrong on my end. Give me a second and try again."
            )
        except Exception:
            pass


def setup_handlers(app: Application, memory: MemoryManager):
    global _memory
    _memory = memory

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("clear", handle_clear))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_error_handler(error_handler)
