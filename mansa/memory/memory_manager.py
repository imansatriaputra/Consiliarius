import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

MEMORY_DIR = Path(__file__).parent

FILES = {
    "core": "mansa_core.json",
    "current": "mansa_current.json",
    "history": "mansa_history.json",
    "memory": "mansa_memory.json",
    "people": "mansa_people.json",
    "decisions": "mansa_decisions.json",
    "goals": "mansa_goals.json",
    "patterns": "mansa_patterns.json",
    "feedback": "mansa_feedback.json",
    "conversations": "mansa_conversations.json",
}

EMPTY_STRUCTURES = {
    "history": {"log": []},
    "memory": {"entries": []},
    "decisions": {"decisions": []},
    "feedback": {"entries": []},
    "conversations": {},
    "patterns": {
        "productivity": [],
        "decision_making": [],
        "content_capture": [],
        "communication_style": [],
        "taste_signals": [],
        "energy_patterns": [],
        "corrections": [],
    },
    "goals": {"goals": []},
    "people": {},
    "current": {},
    "core": {},
}


class MemoryManager:
    def __init__(self):
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        for key, filename in FILES.items():
            path = MEMORY_DIR / filename
            if not path.exists():
                self._write_json(path, EMPTY_STRUCTURES.get(key, {}))

    def _read_json(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: Any):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, key: str) -> Any:
        return self._read_json(MEMORY_DIR / FILES[key])

    def save(self, key: str, data: Any):
        self._write_json(MEMORY_DIR / FILES[key], data)

    # ─── Memory entries ───────────────────────────────────────────────────────

    def add_memory_entry(
        self,
        content: str,
        keywords: Optional[List[str]] = None,
        entry_type: str = "note",
        extra: Optional[Dict] = None,
    ) -> Dict:
        data = self.load("memory")
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "keywords": keywords or [],
            "type": entry_type,
            **(extra or {}),
        }
        data["entries"].append(entry)
        self.save("memory", data)
        return entry

    def search(
        self,
        query: str,
        since_date: Optional[str] = None,
        file_keys: Optional[List[str]] = None,
    ) -> List[Dict]:
        keywords = [k.lower() for k in query.split() if len(k) > 2]
        results = []
        search_keys = file_keys or ["memory", "people", "decisions", "goals", "current", "history"]

        for key in search_keys:
            try:
                data = self.load(key)
                self._search_in_data(data, keywords, key, since_date, results)
            except Exception:
                continue

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:20]

    def _search_in_data(
        self,
        data: Any,
        keywords: List[str],
        source: str,
        since_date: Optional[str],
        results: List[Dict],
    ):
        if isinstance(data, dict):
            if "entries" in data:
                for entry in data["entries"]:
                    self._score_entry(entry, keywords, source, since_date, results)
            elif "decisions" in data:
                for entry in data["decisions"]:
                    self._score_entry(entry, keywords, source, since_date, results)
            elif "log" in data:
                for entry in data["log"]:
                    self._score_entry(entry, keywords, source, since_date, results)
            elif "goals" in data:
                for entry in data["goals"]:
                    self._score_entry(entry, keywords, source, since_date, results)
            else:
                text = json.dumps(data, ensure_ascii=False).lower()
                score = sum(1 for k in keywords if k in text)
                if score > 0:
                    results.append({"source": source, "content": text[:500], "score": score})

    def _score_entry(
        self,
        entry: Dict,
        keywords: List[str],
        source: str,
        since_date: Optional[str],
        results: List[Dict],
    ):
        if since_date and entry.get("timestamp", "") < since_date:
            return
        text = json.dumps(entry, ensure_ascii=False).lower()
        score = sum(1 for k in keywords if k in text)
        stored_keywords = [kw.lower() for kw in entry.get("keywords", [])]
        score += sum(2 for k in keywords if k in stored_keywords)
        if score > 0:
            results.append({
                "source": source,
                "entry": entry,
                "score": score,
                "timestamp": entry.get("timestamp", ""),
            })

    # ─── Current context ──────────────────────────────────────────────────────

    def update_current(self, updates: Dict, reason: str = ""):
        current = self.load("current")
        history = self.load("history")

        for key, new_value in updates.items():
            old_value = current.get(key)
            if old_value != new_value:
                history["log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "field": key,
                    "old_value": old_value,
                    "new_value": new_value,
                    "reason": reason,
                })
            current[key] = new_value

        self.save("current", current)
        self.save("history", history)

    # ─── People ───────────────────────────────────────────────────────────────

    def upsert_person(self, name: str, data: Dict):
        people = self.load("people")
        existing = people.get(name, {})
        existing.update(data)
        existing["last_updated"] = datetime.now().isoformat()
        people[name] = existing
        self.save("people", people)

    def get_person(self, name: str) -> Optional[Dict]:
        people = self.load("people")
        name_lower = name.lower()
        for key, val in people.items():
            if key.lower() == name_lower:
                return val
        return None

    def summarize_people(self) -> str:
        people = self.load("people")
        lines = []
        for name, data in people.items():
            rel = data.get("relationship", "")
            ctx = data.get("context", "")
            lines.append(f"- {name} ({rel}): {ctx}")
        return "\n".join(lines) if lines else "No people logged yet."

    # ─── Decisions ────────────────────────────────────────────────────────────

    def log_decision(
        self,
        options: List[str],
        choice: str,
        reasoning: str,
        context: str = "",
    ):
        decisions = self.load("decisions")
        decisions["decisions"].append({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "options": options,
            "choice": choice,
            "reasoning": reasoning,
        })
        self.save("decisions", decisions)

    # ─── Goals ────────────────────────────────────────────────────────────────

    def get_active_goals(self) -> List[Dict]:
        goals = self.load("goals")
        return [g for g in goals.get("goals", []) if g.get("status") == "active"]

    def update_goal(self, goal_id: str, updates: Dict):
        goals = self.load("goals")
        for goal in goals["goals"]:
            if goal["id"] == goal_id:
                goal.update(updates)
                break
        self.save("goals", goals)

    def add_goal(self, title: str, description: str, target_date: Optional[str] = None) -> str:
        goals = self.load("goals")
        goal_id = f"goal_{str(uuid.uuid4())[:8]}"
        goals["goals"].append({
            "id": goal_id,
            "title": title,
            "description": description,
            "target_date": target_date,
            "status": "active",
            "progress_notes": [],
            "last_checked": None,
        })
        self.save("goals", goals)
        return goal_id

    def format_active_goals(self) -> str:
        goals = self.get_active_goals()
        if not goals:
            return "No active goals logged."
        lines = []
        for g in goals:
            target = f" (target: {g['target_date']})" if g.get("target_date") else ""
            lines.append(f"- {g['title']}{target}: {g.get('description', '')}")
        return "\n".join(lines)

    # ─── Ideas ────────────────────────────────────────────────────────────────

    def save_idea(self, idea_card: Dict):
        ideas_path = MEMORY_DIR.parent / "ideas.json"
        if ideas_path.exists():
            with open(ideas_path, "r", encoding="utf-8") as f:
                ideas = json.load(f)
        else:
            ideas = {"ideas": []}

        idea_card["id"] = str(uuid.uuid4())
        idea_card["timestamp"] = datetime.now().isoformat()
        ideas["ideas"].append(idea_card)

        with open(ideas_path, "w", encoding="utf-8") as f:
            json.dump(ideas, f, indent=2, ensure_ascii=False)

        self.add_memory_entry(
            content=f"Idea captured: {idea_card.get('title', idea_card.get('core_argument', ''))}",
            keywords=["idea", "content"] + idea_card.get("tags", []),
            entry_type="idea",
        )

    # ─── Feedback ─────────────────────────────────────────────────────────────

    def log_feedback(self, original_input: str, mansa_output: str, correction: str):
        feedback = self.load("feedback")
        feedback["entries"].append({
            "timestamp": datetime.now().isoformat(),
            "input": original_input,
            "output": mansa_output,
            "correction": correction,
        })
        self.save("feedback", feedback)

        patterns = self.load("patterns")
        patterns["corrections"].append({
            "timestamp": datetime.now().isoformat(),
            "correction": correction,
        })
        self.save("patterns", patterns)

    # ─── Patterns ─────────────────────────────────────────────────────────────

    def add_pattern_observation(self, pattern_type: str, observation: str):
        patterns = self.load("patterns")
        if pattern_type not in patterns:
            patterns[pattern_type] = []
        patterns[pattern_type].append({
            "timestamp": datetime.now().isoformat(),
            "observation": observation,
        })
        self.save("patterns", patterns)

    def get_recent_patterns(self, limit: int = 10) -> str:
        patterns = self.load("patterns")
        lines = []
        for ptype, entries in patterns.items():
            if entries:
                recent = entries[-3:] if len(entries) >= 3 else entries
                for e in recent:
                    lines.append(f"[{ptype}] {e.get('observation', e.get('correction', ''))}")
        return "\n".join(lines[-limit:]) if lines else ""

    # ─── Conversation history ─────────────────────────────────────────────────

    def get_conversation_history(self, chat_id: str) -> List[Dict]:
        data = self.load("conversations")
        return data.get(str(chat_id), [])

    def add_to_conversation(self, chat_id: str, role: str, content: str):
        data = self.load("conversations")
        key = str(chat_id)
        if key not in data:
            data[key] = []
        data[key].append({"role": role, "content": content})
        if len(data[key]) > 40:
            data[key] = data[key][-40:]
        self.save("conversations", data)

    def clear_conversation(self, chat_id: str):
        data = self.load("conversations")
        data[str(chat_id)] = []
        self.save("conversations", data)
