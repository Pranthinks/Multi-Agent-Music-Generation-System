from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import re

from agents.simplified_agent import SimplifiedAgent
from tools.music_tools import generate_music, get_music_mood_preset
from tools.billing_tools import process_payment, check_subscription_status, list_all_customers
from tools.marketing_tools import get_latest_music, create_music_sample, post_to_social_media


class LangChainMultiAgentSystem:
    """Multi-agent system with 3 specialized agents"""
    
    def __init__(self, api_key: str):
        """Initialize the multi-agent system"""
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0
        )
        
        # Create 3 specialized agents
        self.music_agent = SimplifiedAgent(
            "Music Producer",
            "expert at generating AI music for various moods and styles",
            [generate_music, get_music_mood_preset],
            self.llm
        )
        
        self.billing_agent = SimplifiedAgent(
            "Finance Manager",
            "expert at handling payments and subscription management",
            [process_payment, check_subscription_status, list_all_customers],
            self.llm
        )
        
        self.marketing_agent = SimplifiedAgent(
            "Marketing Manager",
            "social media expert who promotes EXISTING music. CRITICAL: You do NOT generate music - that is the Music Producer's job! You ONLY use existing music files. Always start by using get_latest_music to find existing files, then optionally create samples, and post to social media.",
            [get_latest_music, create_music_sample, post_to_social_media],
            self.llm
        )
        
        print("Multi-Agent System Initialized!")
        print("Music Agent - Ready")
        print("Billing Agent - Ready")
        print("Marketing Agent - Ready")
    
    def _classify_request(self, user_input: str) -> str:
        """Use LLM to classify the request into categories"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a request classifier. Analyze the user's request and respond with ONE word only.

Categories:
- "billing" → payments, fees, charges, subscriptions, customers, money, invoices, costs
- "music" → generating music, creating songs, composing, making tracks
- "marketing" → social media, posting, sharing, promoting on Twitter/Instagram/Facebook
- "other" → anything else (greetings, general questions, unrelated topics)

Respond with ONLY ONE WORD: billing, music, marketing, or other"""),
            ("user", "{input}")
        ])
        
        try:
            messages = prompt.format_messages(input=user_input)
            response = self.llm.invoke(messages)
            category = re.sub(r'[^a-z]', '', response.content.strip().lower())
            
            if category not in ["billing", "music", "marketing", "other"]:
                category = "other"
            
            return category
        except Exception as e:
            print(f"Classification error: {e}")
            return "other"
    
    def _route_to_agent(self, user_input: str):
        """Smart routing with LLM + handles irrelevant questions"""
        
        # Classify the request
        category = self._classify_request(user_input)
        print(f"Classification: {category}")
        
        # Handle irrelevant questions
        if category == "other":
            print(f"Request outside system capabilities")
            
            # Check if it's just a greeting/chitchat
            greetings = ["hello", "hi", "hey", "thanks", "thank you", "bye", "good morning", "good evening"]
            if any(word in user_input.lower() for word in greetings):
                return "greeting"  # Special flag
            
            # For other irrelevant questions, return None to indicate we can't help
            return None
        
        # Route to the correct agent
        agents_map = {
            "music": self.music_agent,
            "billing": self.billing_agent,
            "marketing": self.marketing_agent
        }
        
        agent = agents_map.get(category, self.music_agent)
        print(f"Routing → {agent.name}")
        return agent
    
    def invoke(self, input_dict: dict) -> dict:
        """Process user input through the multi-agent system"""
        user_input = input_dict["input"]
        
        print(f"\n{'='*70}")
        print(f"🤖 SUPERVISOR: Analyzing request...")
        print(f"{'='*70}\n")
        
        # Route to appropriate agent
        agent = self._route_to_agent(user_input)
        
        # Handle greeting
        if agent == "greeting":
            return {
                "output": "Hello! I'm your AI assistant specialized in music generation, billing management, and social media marketing. How can I help you today?"
            }
        
        # Handle irrelevant questions
        if agent is None:
            return {
                "output": """I'm a specialized assistant for music generation, billing, and social media marketing.

I can help you with:
 Music Generation - Create songs in different moods (happy, sad, energetic, etc.)
 Billing & Payments - Process payments, manage subscriptions, check customer status
 Social Media - Post music to Twitter, Instagram, Facebook

Your question seems to be outside these areas. Is there something related to music, billing, or marketing I can help you with?"""
            }
        
        print(f"SUPERVISOR: Delegating to {agent.name}\n")
        
        try:
            # Execute with the selected agent
            output = agent.invoke(user_input)
            
            print(f"\n{'='*70}")
            print(f"SUPERVISOR: Task completed by {agent.name}")
            print(f"{'='*70}\n")
            
            return {"output": output}
            
        except Exception as e:
            error_msg = f"Error in {agent.name}: {str(e)}"
            print(f"\n{error_msg}\n")
            return {"output": error_msg}