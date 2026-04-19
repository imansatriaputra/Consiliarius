import base64
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import httpx
from anthropic import AsyncAnthropic

MODEL = "claude-sonnet-4-6"
MAX_FRAMES = 10
FRAME_INTERVAL_SECONDS = 3

_client: Optional[AsyncAnthropic] = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def _encode_image(file_path: str) -> Tuple[str, str]:
    path = Path(file_path)
    ext = path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(ext, "image/jpeg")
    with open(file_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def _extract_video_frames(video_path: str) -> List[str]:
    try:
        import cv2
    except ImportError:
        return []

    frames_b64 = []
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_step = max(1, int(fps * FRAME_INTERVAL_SECONDS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_extract = min(MAX_FRAMES, total_frames // frame_step + 1)

    extracted = 0
    frame_idx = 0

    while extracted < frames_to_extract and frame_idx < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frames_b64.append(base64.standard_b64encode(buffer).decode("utf-8"))
        extracted += 1
        frame_idx += frame_step

    cap.release()
    return frames_b64


async def analyze_image(
    file_path: str,
    user_context: str = "",
    conversation_context: str = "",
) -> str:
    try:
        image_data, media_type = _encode_image(file_path)
    except Exception:
        return "Can't read that image. Try a clearer shot."

    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            },
        }
    ]

    prompt_parts = []
    if conversation_context:
        prompt_parts.append(f"Context from our conversation: {conversation_context}")
    if user_context:
        prompt_parts.append(f"Iman's note: {user_context}")
    prompt_parts.append(
        "Analyze this image fully. Be direct and specific. "
        "If it's a document, extract the key information. "
        "If it's a product or watch, identify and assess it. "
        "If it's an outfit, give honest style feedback. "
        "If it's a whiteboard or diagram, capture the structure. "
        "Whatever it is — tell Iman what he needs to know."
    )

    content.append({"type": "text", "text": "\n\n".join(prompt_parts)})

    try:
        client = get_client()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Can't read that image. Try a clearer shot."


async def analyze_video(
    file_path: str,
    user_context: str = "",
) -> str:
    frames_b64 = _extract_video_frames(file_path)

    if not frames_b64:
        return "Couldn't extract frames from that video. Either the file is corrupt or opencv isn't installed."

    content = []
    for i, frame_data in enumerate(frames_b64):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": frame_data,
            },
        })
        content.append({
            "type": "text",
            "text": f"[Frame {i + 1} of {len(frames_b64)}]",
        })

    prompt_parts = []
    if user_context:
        prompt_parts.append(f"Iman's note: {user_context}")
    prompt_parts.append(
        f"This is a video analyzed as {len(frames_b64)} sequential frames "
        f"(1 frame every {FRAME_INTERVAL_SECONDS} seconds). "
        "Analyze what's happening across the sequence. Synthesize a coherent response — "
        "don't describe each frame individually unless the differences matter. "
        "Tell Iman what he needs to know."
    )
    content.append({"type": "text", "text": "\n\n".join(prompt_parts)})

    try:
        client = get_client()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text
    except Exception:
        return "Video analysis failed on my end. Try again or send individual frames."


def is_opencv_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False
