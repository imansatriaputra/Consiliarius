# MANSA

MANSA is your personal second brain and AI assistant, running as a Telegram bot. He is not a generic assistant — he is the most capable, always-available version of you: sharp, opinionated, with full context of your life, work, goals, and the people around you. He remembers everything you tell him, tracks your goals without being asked, and speaks like a person who happens to be very good at everything. He runs on Claude, transcribes voice with Groq Whisper, and responds in your chosen voice via ElevenLabs.

---

## Prerequisites

- Python 3.11+
- A Telegram account
- API keys for: Telegram, Anthropic, Groq (optional), ElevenLabs (optional)
- Railway account for deployment (or any VPS/cloud host)

---

## API Key Setup

### 1. Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. "MANSA") and a username (e.g. `mansa_yourname_bot`)
4. BotFather gives you a token — copy it to `TELEGRAM_BOT_TOKEN`

**Get your Chat ID:**
1. Message **@userinfobot** on Telegram
2. It replies with your user ID — copy it to `TELEGRAM_CHAT_ID`
3. Setting this restricts MANSA to only respond to you. Strongly recommended.

### 2. Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to **API Keys** → **Create Key**
4. Copy to `ANTHROPIC_API_KEY`

### 3. Groq API Key (voice transcription)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free tier available)
3. Navigate to **API Keys** → create one
4. Copy to `GROQ_API_KEY`

Without this, MANSA can't transcribe voice notes. Text and image capabilities still work.

### 4. ElevenLabs API Key (voice responses)

1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Create an account (free tier available)
3. Go to **Profile** → **API Key**
4. Copy to `ELEVENLABS_API_KEY`

Without this, MANSA responds in text only. Everything else still works.

### 5. Finding Your ElevenLabs Voice ID

1. Log in to [elevenlabs.io](https://elevenlabs.io)
2. Go to **Voices** in the left sidebar
3. Browse the Voice Library or your saved voices
4. Click on a voice you want MANSA to use
5. Click **"Add to Voice Lab"** if it's from the library
6. Go to **Voice Lab** → find your voice → click the **ID** icon (looks like `</>`) next to the voice name, or find it in the URL
7. Alternatively: go to **Voice Lab**, click any voice, and the voice ID appears in the API snippet shown on the right panel
8. Copy the ID (format: `21m00Tcm4TlvDq8ikWAM`) to `ELEVENLABS_VOICE_ID`

**Recommended voice profile for MANSA:** A confident, natural male voice. Search for "Adam", "Josh", or "Antoni" in the Voice Library as starting points.

---

## Local Setup

```bash
# 1. Clone the repo and navigate to the mansa directory
cd mansa

# 2. Create a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your actual API keys

# 5. Run MANSA
python main.py
```

You should see:
```
MANSA is online.
Starting MANSA...
```

Open Telegram, message your bot, and MANSA responds.

---

## Testing Locally

Send these to your bot to verify everything works:

| Test | What to send | Expected |
|------|-------------|----------|
| Basic response | "What's on my plate right now?" | MANSA summarizes your current context |
| Memory save | "Remember that I had coffee with Ahmed today" | "Stored." |
| Goal review | "Review my goals" | Status check on all active goals |
| Identity query | "What do you know about me?" | Summary from core + current files |
| Voice note | Send a voice message | Transcription + response |
| Image | Send a photo | Analysis + response |
| System check | `/status` | Shows which APIs are active |

---

## Railway Deployment (Step by Step)

Railway is the recommended host. MANSA runs as a background worker (no HTTP server needed).

### Step 1 — Push your code to GitHub

Make sure your repo is on GitHub (or GitLab/Bitbucket).

### Step 2 — Create a Railway project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway auto-detects the project

### Step 3 — Set the root directory

1. In your Railway project, go to your service
2. Click **Settings**
3. Under **Source**, set **Root Directory** to `mansa`
4. This tells Railway to treat `mansa/` as the project root

### Step 4 — Add environment variables

1. In your Railway service, go to **Variables**
2. Add each variable from `.env.example`:
   - `TELEGRAM_BOT_TOKEN`
   - `ANTHROPIC_API_KEY`
   - `TELEGRAM_CHAT_ID`
   - `GROQ_API_KEY` (optional)
   - `ELEVENLABS_API_KEY` (optional)
   - `ELEVENLABS_VOICE_ID` (optional)

### Step 5 — Deploy

1. Click **Deploy** (or Railway auto-deploys on push)
2. Watch the build logs — nixpacks installs dependencies automatically
3. Once deployed, check **Logs** tab — you should see `MANSA is online.`

### Step 6 — Verify

Message your Telegram bot. MANSA should respond within a few seconds.

**Railway tips:**
- The free tier has usage limits — check your plan
- Enable **Restart on Failure** (already set in `railway.toml`)
- MANSA uses minimal memory and CPU — the smallest Railway instance works fine

---

## How to Use MANSA

MANSA understands natural language. No slash commands required for most things.

### Memory

```
"Remember that I parked on level 3, space B7"
→ Stored.

"Log this: I decided to push the Mastercard comp anchor to 180M IDR"
→ Got it, logged.

"MANSA note that the Seamaster needs a strap change"
→ Stored.

"What did I say about the Mastercard salary negotiation?"
→ Searches all memory and retrieves relevant context

"Where did I put my passport?"
→ Searches memory for any mention of your passport
```

### Identity & Context

```
"What do you know about me?"
→ Summary from your core + current context files

"What have I been working on?"
→ Active projects from current context + recent memory

"What was I focused on last month?"
→ Searches history log with timestamp filtering
```

### Goals

```
"Review my goals"
→ Status check on all active goals, calls out drift

"Add a new goal: finish the Mastercard negotiation by end of month"
→ Logs a new active goal
```

### Decisions

```
"Log a decision"
→ MANSA asks for options, choice, and reasoning. Saves to decisions.json.
```

### People Briefings

```
"Brief me on Loan"
→ Full context on Loan from people.json — relationship, history, last interaction

"I just had a call with Ahmed — he advised me to anchor higher"
→ Saves the interaction detail. MANSA may ask if you want to update the people record.
```

### Ideas

```
"New idea: brands that master emotional resonance in data marketing outperform on retention"
→ MANSA structures it into an idea card with core argument, credibility angle, 
  audience, tension, content angles, and his honest take.
  Asks if you want to save it.
```

### Media

```
Voice note → Transcribed via Groq Whisper, processed as text, saved to memory
Photo → Analyzed by Claude vision (outfit, document, watch, whiteboard, anything)
Video → Frames extracted, analyzed sequentially, synthesized response
```

### Scheduled Briefings

- **Every day at 7:00 AM WIB**: Morning briefing — priority, something to think about, content idea, people context
- **Every Sunday at 8:00 AM WIB**: Weekly review — patterns, goal drift, what MANSA wants to improve at

### Bot Commands

| Command | What it does |
|---------|-------------|
| `/start` | Wakes MANSA up |
| `/clear` | Clears conversation history (memory files preserved) |
| `/status` | Shows which APIs are active |

---

## How the Memory System Works

MANSA's memory is stored as JSON files in the `memory/` directory. Every piece of context is persisted — nothing lives only in RAM.

| File | Purpose | Changes when |
|------|---------|-------------|
| `mansa_core.json` | Foundational identity — who you are, how you think, values | You explicitly redefine something fundamental |
| `mansa_current.json` | Living context — role, projects, career status, priorities | Life evolves |
| `mansa_history.json` | Append-only log of every change to `mansa_current.json` | `mansa_current.json` changes |
| `mansa_memory.json` | Every specific detail ever told to MANSA | Every interaction that contains a fact |
| `mansa_people.json` | Key people with full context | You mention someone or ask for updates |
| `mansa_decisions.json` | Log of significant decisions with options and reasoning | You log a decision |
| `mansa_goals.json` | Active goals with status and progress notes | Goals are added, updated, or completed |
| `mansa_patterns.json` | How MANSA learns your behavior over time | Silently, as MANSA observes |
| `mansa_feedback.json` | Every time you corrected MANSA's output | You explicitly correct something |
| `mansa_conversations.json` | Last 40 messages per chat for context window | Every message |

### How MANSA Saves Memory

MANSA saves memory in two ways:

1. **Explicit commands** — "remember this", "log this", "MANSA note that" trigger immediate saves
2. **Auto-detection** — When you state a fact about your life, MANSA embeds a save action in his response using internal tags that are processed automatically before you see the response

For routine saves, MANSA confirms with exactly two words: **"Stored."** or **"Got it, logged."**

### Memory Search

When you ask "what did I say about X" or "where did I put Y", MANSA searches across all memory files using keyword matching and timestamp filtering. The most relevant results surface first.

### System Prompt Construction

Every Claude API call builds a fresh system prompt from:
1. MANSA's personality (hardcoded)
2. `mansa_core.json` (full)
3. `mansa_current.json` (full)
4. `mansa_people.json` (summarized)
5. `mansa_goals.json` (active goals only)
6. Last 20 message exchanges (from `mansa_conversations.json`)

This means MANSA always has your freshest context without retraining.

---

## Troubleshooting

**MANSA doesn't respond**
- Check Railway logs for errors
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Make sure `TELEGRAM_CHAT_ID` matches your actual ID (message @userinfobot to check)

**"Missing required environment variables" on startup**
- `TELEGRAM_BOT_TOKEN` and `ANTHROPIC_API_KEY` are required
- All others are optional but voice features need their respective keys

**Voice transcription not working**
- Confirm `GROQ_API_KEY` is set correctly
- Groq free tier has rate limits — wait a minute and retry
- Check Railway logs for the specific error

**ElevenLabs voice not sending**
- Both `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` must be set
- Verify the voice ID exists in your ElevenLabs account
- ElevenLabs free tier has monthly character limits
- MANSA only sends voice for responses under 1000 characters to stay within limits

**Video processing fails**
- Requires `opencv-python-headless` — confirm it's in requirements.txt
- Railway's nixpacks build may need system libraries — they're listed in `nixpacks.toml`
- Check logs for the specific OpenCV error

**Memory files getting large**
- `mansa_memory.json` is append-only and grows over time — this is by design
- If it becomes unwieldy, manually archive old entries
- `mansa_conversations.json` is capped at 40 messages per chat automatically

**Scheduler not running (no morning briefing)**
- `TELEGRAM_CHAT_ID` must be set — scheduler is disabled without it
- Check Railway logs for `"Scheduler running for chat_id..."`
- Timezone is Asia/Jakarta (WIB) — briefing at 07:00, weekly review Sunday 08:00

**"Something went wrong on my end" from MANSA**
- Usually an Anthropic API error — check your API key and usage limits
- Check Railway logs for the actual exception

**Railway build fails**
- Confirm Root Directory is set to `mansa` in Railway settings
- Check that `nixpacks.toml` is present in the `mansa/` directory
- Review build logs for the specific package that failed
