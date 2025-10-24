# 🎵 AI Music Generator Company

An autonomous music generation company powered by multi-agent AI system. Generate music, handle billing, and market on social media - all automated!

## 🎯 Goal

Build an autonomous music generation company with AI music creation, billing management, and social media marketing.

## ✨ Features

### Core Agents

- **🎵 Music Agent** - Generates AI music daily using Riffusion.
- **💰 Billing Agent** - Handles monthly subscription payments ($1/month) - Created a dummy .json database.
- **📱 Marketing Agent** - Posts music to social media (Twitter, Instagram, Facebook) with samples

### Bonus Features

- **Mood-based music generation** - Create music for different moods (happy, sad, energetic, calm, epic, chill)

## Tech Stack

- **Backend**: Flask, LangChain, Google Gemini 2.0
- **AI Music**: HuggingFace ACE-Step API (Suno-style generation)
- **Agents**: Multi-agent system with specialized roles
- **Data**: JSON file database

## 🤖 How the Autonomous System Works

The system runs three specialized AI agents:

1. **Music Agent** 
   - Generates AI music daily
   - Supports multiple moods and styles
   - Uses HuggingFace API for music generation

2. **Billing Agent**
   - Processes $1 monthly subscriptions
   - Manages customer database
   - Tracks payment history

3. **Marketing Agent**
   - Finds latest generated music
   - Creates 30-second preview samples
   - Posts to social media platforms with engaging captions
   - *Note: Currently simulated - real social media APIs can be integrated*

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Environment File

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key_here
```

Get your API key from: https://aistudio.google.com/app/apikey

### 3. Project Structure


```
project/
├── app.py                      # Flask web server
├── scheduler.py                # Automated tasks
├── agents/
│   ├── multi_agent_system.py  # Agent coordinator
│   └── simplified_agent.py    # Agent implementation
├── tools/
│   ├── music_tools.py         # Music generation
│   ├── billing_tools.py       # Payment processing
│   └── marketing_tools.py     # Social media posting
├── templates/
│   └── index.html             # Web interface UI
├── utils/
│   └── database.py            # Database helper functions
├── customer_database.json     # Customer data
└── generated_music/           # Generated music files
```

## Usage

### Run Web App (Interactive Mode)

```bash
python app.py
```

Open http://localhost:5000 in your browser

**Features:**
- Chat interface to interact with agents
- View all customers and their status
- Browse generated music files
- Quick action buttons for common tasks

### Run Scheduler (Autonomous Mode)

```bash
python scheduler.py
```

**Automated Tasks:**
- 🎵 Daily music generation (configurable schedule)
- 📱 Daily social media posting (configurable schedule)
- 💰 Monthly billing for all customers (configurable schedule)

This runs the company autonomously - generating music, posting it, and billing customers automatically!

## Example Commands

**Generate Music (Mood-based):**
- "Generate a happy uplifting song"
- "Create sad melancholic music"
- "Make an energetic workout track"
- "Generate calm meditation music"
- "Create epic cinematic music"
- "Make chill lo-fi beats"
You can enter any mood based prompt, I had used LLM to classify your prompt into on of the category.

**Billing:**
- "Process payment of $1 for John Doe"


**Marketing:**
- "Post latest music to social media"
- "Create a sample and post to Instagram"

## How It Works

1. **User Input** → System classifies request (music/billing/marketing)
2. **Agent Selection** → Routes to specialized agent
3. **Tool Execution** → Agent uses tools to complete task
4. **Response** → Returns result to user

## Notes

- Subscription is $1/month per customer
- Music generation uses free HuggingFace API (may have rate limits)
- Database is JSON file-based for simplicity
- **Social media posting is currently simulated** - Real Twitter/Instagram/Facebook APIs can be integrated by replacing the print statements with actual API calls
- Scheduler can be customized for different time intervals
- All agents work autonomously once configured

## Bonus Features Included

- ✅ Mood-based music generation (Implemented) _ You can open the UI and 
enter your mood based prompt and it gonna generate the relevant music.

## Troubleshooting

**"GPU quota exceeded"** - As we are using free version Riffusion we have a limited music generation access.

**"API Key error"** - Check your `.env` file has correct GOOGLE_API_KEY, even free version of gemini api has limited calls.

**No music files** - Generate music first before posting to social media

---

