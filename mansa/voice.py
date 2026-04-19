import io
import os
import tempfile
from pathlib import Path
from typing import Optional

_groq_client = None
_eleven_client = None


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client


def get_eleven_client():
    global _eleven_client
    if _eleven_client is None:
        from elevenlabs.client import ElevenLabs
        _eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    return _eleven_client


async def transcribe_voice(file_path: str) -> Optional[str]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        client = get_groq_client()
        path = Path(file_path)
        suffix = path.suffix.lower() or ".ogg"

        content_type_map = {
            ".ogg": "audio/ogg",
            ".mp3": "audio/mpeg",
            ".mp4": "audio/mp4",
            ".m4a": "audio/mp4",
            ".wav": "audio/wav",
            ".webm": "audio/webm",
            ".flac": "audio/flac",
        }
        content_type = content_type_map.get(suffix, "audio/ogg")

        with open(file_path, "rb") as f:
            audio_data = f.read()

        transcription = client.audio.transcriptions.create(
            file=(path.name, audio_data, content_type),
            model="whisper-large-v3",
            response_format="text",
        )

        if isinstance(transcription, str):
            return transcription.strip()
        return transcription.text.strip() if hasattr(transcription, "text") else str(transcription).strip()

    except Exception as e:
        error_str = str(e).lower()
        if "api" in error_str or "auth" in error_str:
            return None
        return None


async def generate_voice_response(text: str) -> Optional[bytes]:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")

    if not api_key or not voice_id:
        return None

    try:
        client = get_eleven_client()
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        audio_bytes = b"".join(audio_stream)
        return audio_bytes if audio_bytes else None

    except Exception:
        return None


def is_groq_available() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def is_elevenlabs_available() -> bool:
    return bool(os.getenv("ELEVENLABS_API_KEY")) and bool(os.getenv("ELEVENLABS_VOICE_ID"))
