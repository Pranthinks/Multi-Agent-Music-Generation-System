# Multi-Agent Music Generation System

An intelligent AI system that automates music generation, subscription management, and social media marketing using a multi-agent architecture.

## 🎯 Overview

This project implements a **3-agent system with supervisor pattern** that handles:
- 🎵 AI Music Generation
- 💳 Payment & Subscription Management  
- 📱 Social Media Marketing Automation

## 🏗️ Architecture

**Supervisor Agent** - Routes requests to specialized agents using LLM-based classification

**Specialized Agents:**
1. **Music Producer** - Generates AI music with custom moods and styles
2. **Finance Manager** - Processes payments and manages customer subscriptions
3. **Marketing Manager** - Promotes music on social media platforms

## 🚀 Features

- Generate music with customizable moods (happy, sad, energetic, calm, epic, chill)
- Process $1/month subscription payments
- Track customer data in JSON database
- Automated social media posting (Twitter, Instagram, Facebook)
- Intelligent request routing with LLM classification

## 🛠️ Tech Stack

- **LangChain** - Agent framework
- **Google Gemini 2.0 Flash** - LLM for reasoning and classification
- **HuggingFace ACE-Step** - Music generation API
- **Gradio Client** - API integration

## 📦 Installation
```bash
pip install langchain langchain-google-genai gradio-client
```

## ⚙️ Setup

1. Create a `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

2. Run the system:
```python
from your_module import create_langchain_multiagent_system

system = create_langchain_multiagent_system(api_key="your_key")
response = system.invoke({"input": "Generate a happy song"})
```

## 📝 Usage Examples
```python
# Generate music
"Create an energetic song for my workout"

# Check subscription
"What's the status of John Doe's subscription?"

# Social media post
"Post my latest music to Instagram"
```

## 🗂️ Project Structure
```
├── music_agent (Music generation tools)
├── billing_agent (Payment processing tools)
├── marketing_agent (Social media tools)
└── supervisor (Request classification & routing)
```

## 📄 License

MIT License