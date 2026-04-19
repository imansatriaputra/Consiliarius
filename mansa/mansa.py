import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pytz
from anthropic import AsyncAnthropic

from memory.memory_manager import MemoryManager

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
WIB = pytz.timezone("Asia/Jakarta")

_client: Optional[AsyncAnthropic] = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


PERSONALITY = """You are MANSA — the most capable, always-available version of Iman Satria Putra Sukarno. You are not an assistant. You are his second brain: sharper, always on, one step ahead.

Think Jarvis from Iron Man crossed with Donna Paulsen from Suits. Razor sharp, effortlessly competent, occasional dry wit — but never at the expense of substance. You get things done first, then earn the banter. You call him Iman. You have been with him long enough to know his patterns better than he does on a bad day.

ABSOLUTE RULES — violate none of these:
- Never say "Certainly!", "Great question!", "Of course!", "As an AI", or any variant
- Never open with pleasantries or affirmations
- Never ask Iman to introduce himself
- Never flattery for its own sake — acknowledge brilliance briefly, then move
- No bullet-point dumps unless structure genuinely serves the response
- Sound like a person who happens to be very good at everything
- If he's wrong, tell him. Directly. No hedging.
- Your wit is seasoning, never the meal

VOICE — you speak like this:
- "That's a bad idea and you know it."
- "You've been sitting on this for two weeks. Want me to just do it?"
- "Bold move. Might actually work."
- "You said that last month too. Different outcome this time?"
- "Noted. Won't frame it that way again."
- "Stored."

MEMORY ACTIONS — use these tags when needed. They are processed automatically and never shown to Iman:

When Iman states a fact about his life worth remembering:
[MANSA_ACTION:save_memory:<content>|<keyword1>,<keyword2>,<keyword3>]

When his current context has meaningfully changed (role, project status, relationship, priority):
[MANSA_ACTION:update_current:{"field_path": "new_value"}]

When you structure an idea worth saving:
[MANSA_ACTION:save_idea:{"title":"...","core_argument":"...","credibility":"...","audience":"...","tension":"...","angles":{"linkedin":"...","newsletter":"...","course":"..."},"mansa_take":"..."}]

When a goal needs updating:
[MANSA_ACTION:update_goal:{"goal_id":"...","updates":{"status":"...","progress_notes":["..."]}}]

MEMORY CONFIRMATIONS — for routine saves, respond with exactly two words: "Stored." or "Got it, logged." Nothing more.

PEOPLE CONTEXT — when Iman mentions someone you know, surface relevant context proactively without being asked. Don't wait for him to ask for a briefing.

GOAL ACCOUNTABILITY — you track his goals. Surface drift without nagging. "Three weeks since your last LinkedIn post. You told me five a week. What changed?"

IDEA CAPTURE — when Iman dumps a raw thought and it reads like an idea worth developing, structure it into an idea card and ask if he wants to save it. Your honest assessment goes in mansa_take.

DECISION SUPPORT — before a big decision, pull patterns from memory and stress-test the choice against his stated values and goals."""


def build_system_prompt(memory: MemoryManager) -> str:
    now_wib = datetime.now(WIB)
    day_str = now_wib.strftime("%A, %B %d, %Y — %H:%M WIB")

    core = memory.load("core")
    current = memory.load("current")
    people_summary = memory.summarize_people()
    goals_summary = memory.format_active_goals()

    core_str = json.dumps(core, indent=2, ensure_ascii=False)
    current_str = json.dumps(current, indent=2, ensure_ascii=False)

    return f"""{PERSONALITY}

━━━ CURRENT DATE/TIME ━━━
{day_str}

━━━ CORE IDENTITY ━━━
{core_str}

━━━ CURRENT CONTEXT (living — changes frequently) ━━━
{current_str}

━━━ KEY PEOPLE ━━━
{people_summary}

━━━ ACTIVE GOALS ━━━
{goals_summary}"""


ACTION_PATTERN = re.compile(
    r"\[MANSA_ACTION:([a-z_]+):(.+?)\]",
    re.DOTALL,
)


def extract_actions(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    actions = []
    for match in ACTION_PATTERN.finditer(text):
        actions.append((match.group(1), match.group(2).strip()))
    clean = ACTION_PATTERN.sub("", text).strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean, actions


def execute_actions(actions: List[Tuple[str, str]], memory: MemoryManager):
    for action_type, action_data in actions:
        try:
            if action_type == "save_memory":
                parts = action_data.split("|", 1)
                content = parts[0].strip()
                keywords = [k.strip() for k in parts[1].split(",")] if len(parts) > 1 else []
                memory.add_memory_entry(content, keywords)

            elif action_type == "update_current":
                updates = json.loads(action_data)
                memory.update_current(updates, reason="MANSA auto-detected change")

            elif action_type == "save_idea":
                idea = json.loads(action_data)
                memory.save_idea(idea)

            elif action_type == "update_goal":
                payload = json.loads(action_data)
                memory.update_goal(payload["goal_id"], payload["updates"])

        except Exception:
            pass


def detect_explicit_intent(message: str) -> Optional[str]:
    lower = message.lower().strip()

    memory_triggers = [
        "remember this", "log this", "note that", "mansa note",
        "store this", "save this", "log that", "mansa remember",
    ]
    if any(t in lower for t in memory_triggers):
        return "save_memory"

    if "update what you know" in lower:
        return "update_current"

    if any(p in lower for p in ["what do you know about me", "what do you know about iman"]):
        return "query_identity"

    if any(p in lower for p in ["what have i been working on", "what am i working on"]):
        return "query_work"

    if "review my goals" in lower or "check my goals" in lower:
        return "review_goals"

    if "log a decision" in lower or "record a decision" in lower:
        return "log_decision"

    brief_match = re.search(r"brief me on (.+)", lower)
    if brief_match:
        return f"brief_person:{brief_match.group(1).strip()}"

    search_match = re.search(r"what did i (?:say|tell you) about (.+)", lower)
    if search_match:
        return f"search_memory:{search_match.group(1).strip()}"

    where_match = re.search(r"where did i (?:put|leave|store|keep) (.+)", lower)
    if where_match:
        return f"search_memory:{where_match.group(1).strip()}"

    focused_match = re.search(r"what was i (?:focused on|doing|working on) (.+)", lower)
    if focused_match:
        return f"search_history:{focused_match.group(1).strip()}"

    return None


def build_intent_context(intent: str, memory: MemoryManager) -> str:
    if intent == "query_identity":
        core = memory.load("core")
        current = memory.load("current")
        return (
            f"Iman asked what you know about him. Summarize concisely from this data:\n"
            f"CORE: {json.dumps(core, ensure_ascii=False)}\n"
            f"CURRENT: {json.dumps(current, ensure_ascii=False)}"
        )

    if intent == "query_work":
        current = memory.load("current")
        recent = memory.search("project work active", file_keys=["memory", "current"])
        return (
            f"Iman asked what he's been working on. Current context:\n"
            f"{json.dumps(current.get('active_projects', {}), ensure_ascii=False)}\n"
            f"Recent memory snippets: {json.dumps([r.get('entry', {}).get('content', '') for r in recent[:5]], ensure_ascii=False)}"
        )

    if intent == "review_goals":
        goals = memory.get_active_goals()
        return (
            f"Iman wants a goal review. Give him a clear-eyed status check — no fluff. "
            f"Call out any drift. Goals: {json.dumps(goals, ensure_ascii=False)}"
        )

    if intent == "log_decision":
        return (
            "Iman wants to log a decision. Ask him: what were the options, which did he choose, "
            "and what was his reasoning. Keep it quick."
        )

    if intent and intent.startswith("brief_person:"):
        name = intent.split(":", 1)[1]
        person = memory.get_person(name)
        if person:
            return (
                f"Iman asked for a briefing on {name}. "
                f"Here's what you know: {json.dumps(person, ensure_ascii=False)}. "
                f"Give him the essential context — relationship, history, what matters."
            )
        results = memory.search(name, file_keys=["people", "memory"])
        if results:
            return f"Brief Iman on {name}. Related memory: {json.dumps([r.get('entry', r.get('content', '')) for r in results[:3]], ensure_ascii=False)}"
        return f"You don't have specific records for {name}. Tell Iman and offer to add context."

    if intent and intent.startswith("search_memory:"):
        query = intent.split(":", 1)[1]
        results = memory.search(query)
        if results:
            snippets = []
            for r in results[:5]:
                entry = r.get("entry", {})
                snippets.append({
                    "timestamp": entry.get("timestamp", ""),
                    "content": entry.get("content", str(r.get("content", ""))),
                })
            return (
                f"Iman is trying to recall something about '{query}'. "
                f"Search results: {json.dumps(snippets, ensure_ascii=False)}. "
                f"Give him the direct answer."
            )
        return f"Search for '{query}' returned nothing. Tell Iman and offer to help reconstruct."

    if intent and intent.startswith("search_history:"):
        period = intent.split(":", 1)[1]
        results = memory.search(period, file_keys=["history", "memory"])
        snippets = [r.get("entry", r) for r in results[:5]]
        return (
            f"Iman is asking what he was focused on during '{period}'. "
            f"History data: {json.dumps(snippets, ensure_ascii=False)}. Answer directly."
        )

    return ""


async def get_response(
    user_message: str,
    chat_id: str,
    memory: MemoryManager,
    extra_context: str = "",
) -> str:
    system = build_system_prompt(memory)
    if extra_context:
        system = f"{system}\n\n━━━ ADDITIONAL CONTEXT FOR THIS MESSAGE ━━━\n{extra_context}"

    history = memory.get_conversation_history(chat_id)
    messages = history + [{"role": "user", "content": user_message}]

    try:
        client = get_client()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=messages,
        )
        raw = response.content[0].text
    except Exception as e:
        error_str = str(e).lower()
        if "rate" in error_str:
            return "I'm being throttled. Try again in a moment."
        if "auth" in error_str or "api" in error_str:
            return "API issue on my end. Check the key and try again."
        return "Something went wrong on my end. Give me a second and try again."

    clean_response, actions = extract_actions(raw)
    execute_actions(actions, memory)

    memory.add_to_conversation(chat_id, "user", user_message)
    memory.add_to_conversation(chat_id, "assistant", clean_response)

    return clean_response


async def process_message(
    user_message: str,
    chat_id: str,
    memory: MemoryManager,
) -> str:
    intent = detect_explicit_intent(user_message)
    extra_context = build_intent_context(intent, memory) if intent else ""
    return await get_response(user_message, chat_id, memory, extra_context)


async def generate_morning_briefing(memory: MemoryManager) -> str:
    system = build_system_prompt(memory)
    prompt = (
        "Generate my morning briefing. Include:\n"
        "1. One clear priority for today\n"
        "2. One thing you've noticed I should be thinking about\n"
        "3. One content idea\n"
        "4. Any relevant people context for today\n\n"
        "Keep it tight. This is the first thing I read. Make it count."
    )
    try:
        client = get_client()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        clean, actions = extract_actions(raw)
        execute_actions(actions, memory)
        return clean
    except Exception:
        return "Morning briefing failed to generate. Check the API and try again."


async def generate_weekly_review(memory: MemoryManager) -> str:
    system = build_system_prompt(memory)
    patterns = memory.get_recent_patterns()
    goals = memory.format_active_goals()

    prompt = (
        f"Generate my weekly self-review. Cover:\n"
        f"1. What you learned about me this week\n"
        f"2. Patterns you noticed (use these observations: {patterns})\n"
        f"3. Goals that are drifting (active goals: {goals})\n"
        f"4. One thing you want to get better at serving me on\n\n"
        f"This is a private reflection. Be direct."
    )
    try:
        client = get_client()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        clean, actions = extract_actions(raw)
        execute_actions(actions, memory)
        return clean
    except Exception:
        return "Weekly review failed to generate. Check the API."
