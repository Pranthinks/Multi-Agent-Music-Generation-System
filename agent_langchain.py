from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from gradio_client import Client
import shutil
from datetime import datetime
import os
import json
import re

DB_FILE = "customer_database.json"

def load_database():
    """Load customer database from file"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"customers": {}}

def save_database(db):
    """Save customer database to file"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

# ===================== MUSIC AGENT TOOLS =====================

@tool
def generate_music(tags: str, lyrics: str, duration: int = 15) -> str:
    """Generates AI music with custom parameters.
    
    Args:
        tags: Music style descriptors (e.g., "upbeat, cheerful, bright")
        lyrics: Song lyrics in format "[verse]\\nLyrics\\n[chorus]\\nMore lyrics"
        duration: Duration in seconds (default: 15)
    
    Returns:
        Path to generated music file
    """
    print(f"\n{'='*60}")
    print(f"🎵 MUSIC GENERATION STARTED")
    print(f"{'='*60}")
    print(f"   Duration: {duration}s")
    print(f"   Tags: {tags[:80]}...")
    print(f"   Lyrics: {lyrics[:80]}...")
    print(f"{'='*60}\n")
    
    try:
        print("📡 Connecting to HuggingFace API...")
        client = Client("ACE-Step/ACE-Step")
        print("✅ Connected successfully")
        
        print("🎼 Sending generation request...")
        result = client.predict(
            audio_duration=duration, prompt=tags, lyrics=lyrics,
            infer_step=60, guidance_scale=15, scheduler_type="euler",
            cfg_type="apg", omega_scale=10, manual_seeds=None,
            guidance_interval=0.5, guidance_interval_decay=0,
            min_guidance_scale=3, use_erg_tag=True, use_erg_lyric=False,
            use_erg_diffusion=True, oss_steps=None, guidance_scale_text=0,
            guidance_scale_lyric=0, audio2audio_enable=False,
            ref_audio_strength=0.5, ref_audio_input=None,
            lora_name_or_path="none", api_name="/__call__"
        )
        
        print("✅ Generation completed")
        
        audio_path, metadata = result
        os.makedirs("generated_music", exist_ok=True)
        output_path = f"generated_music/music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        shutil.copy(audio_path, output_path)
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS: Music saved to {output_path}")
        print(f"{'='*60}\n")
        
        return f"✅ Music generated successfully: {output_path}"
        
    except Exception as e:
        error_msg = str(e)
        
        print(f"\n{'='*60}")
        print(f"❌ MUSIC GENERATION FAILED")
        print(f"{'='*60}")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {error_msg}")
        print(f"{'='*60}\n")
        
        # Provide user-friendly error messages
        if "quota" in error_msg.lower() or "gpu" in error_msg.lower():
            return f"❌ GPU quota exceeded. The free HuggingFace service is currently at capacity. Please try again in 5-10 minutes or use a shorter duration (5-10 seconds)."
        elif "timeout" in error_msg.lower():
            return f"❌ Request timeout. The service is busy. Please wait a few minutes and try again."
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            return f"❌ Network error. Please check your internet connection and try again."
        else:
            return f"❌ Error generating music: {error_msg[:200]}"

@tool
def get_music_mood_preset(mood: str) -> str:
    """Get preset tags and lyrics for a specific mood.
    
    Args:
        mood: Desired mood (happy, sad, energetic, calm, epic, chill)
    
    Returns:
        JSON string with 'tags' and 'lyrics' for the mood
    """
    presets = {
        "happy": {
            "tags": "upbeat, cheerful, bright, major key, 120 BPM",
            "lyrics": "[verse]\\nFeeling good today\\n[chorus]\\nHappiness all the way"
        },
        "sad": {
            "tags": "melancholic, emotional, slow, minor key, 70 BPM",
            "lyrics": "[verse]\\nQuiet moments here\\n[chorus]\\nFeeling all the tears"
        },
        "energetic": {
            "tags": "fast, powerful, intense, driving, 140 BPM",
            "lyrics": "[verse]\\nFull of energy\\n[chorus]\\nUnstoppable velocity"
        },
        "calm": {
            "tags": "peaceful, ambient, relaxing, meditation, 80 BPM",
            "lyrics": "[verse]\\nCalm and serene\\n[chorus]\\nPeaceful scene"
        },
        "epic": {
            "tags": "cinematic, orchestral, dramatic, powerful, 110 BPM",
            "lyrics": "[verse]\\nRising to the heights\\n[chorus]\\nEpic in our sights"
        },
        "chill": {
            "tags": "lo-fi, relaxed, smooth, laid-back, 90 BPM",
            "lyrics": "[verse]\\nTaking it easy\\n[chorus]\\nFeeling breezy"
        }
    }
    
    mood = mood.lower()
    if mood in presets:
        return json.dumps(presets[mood])
    else:
        return json.dumps({"error": f"Unknown mood: {mood}. Available: {', '.join(presets.keys())}"})


# ===================== BILLING AGENT TOOLS =====================

@tool
def process_payment(amount: float, customer_name: str) -> str:
    """Processes monthly payment and updates customer database.
    
    Args:
        amount: Payment amount (must be 1.0 for $1/month subscription)
        customer_name: Full name of the customer
    
    Returns:
        Payment confirmation with details
    """
    print("💳 Processing payment...")
    
    if amount != 1.0:
        return f"❌ Invalid amount. Subscription is $1/month (received: ${amount})"
    
    db = load_database()
    now = datetime.now()
    payment_id = f"PAY_{now.strftime('%Y%m%d%H%M%S')}"
    
    if customer_name not in db["customers"]:
        db["customers"][customer_name] = {
            "status": "active",
            "payments": [],
            "created_at": now.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    db["customers"][customer_name]["payments"].append({
        "amount": amount,
        "payment_id": payment_id,
        "timestamp": now.strftime('%Y-%m-%d %H:%M:%S')
    })
    db["customers"][customer_name]["status"] = "active"
    db["customers"][customer_name]["last_payment"] = now.strftime('%Y-%m-%d %H:%M:%S')
    
    save_database(db)
    
    return f"✅ Payment processed for {customer_name}!\n- Amount: ${amount}\n- Payment ID: {payment_id}\n- Status: Active"

@tool
def check_subscription_status(customer_name: str) -> str:
    """Checks real subscription status from database.
    
    Args:
        customer_name: Full name of the customer
    
    Returns:
        Subscription status details
    """
    print("🔍 Checking subscription...")
    
    db = load_database()
    
    if customer_name not in db["customers"]:
        return f"❌ Customer '{customer_name}' not found in system.\nPlease process payment first to activate subscription."
    
    customer = db["customers"][customer_name]
    status = customer.get("status", "inactive")
    payment_count = len(customer.get("payments", []))
    last_payment = customer.get("last_payment", "Never")
    
    if status == "active":
        return f"✅ {customer_name}: Active subscription\n- Plan: $1/month\n- Total payments: {payment_count}\n- Last payment: {last_payment}"
    else:
        return f"⚠️ {customer_name}: Inactive subscription\n- Total payments: {payment_count}\n- Status: Payment required"

@tool
def list_all_customers() -> str:
    """Lists all customers in the database with their status.
    
    Returns:
        List of all customers and their subscription status
    """
    print("📋 Listing all customers...")
    
    db = load_database()
    customers = db.get("customers", {})
    
    if not customers:
        return "No customers found in the system."
    
    result = f"Total Customers: {len(customers)}\n\n"
    for name, data in customers.items():
        status = data.get("status", "inactive")
        payments = len(data.get("payments", []))
        last_payment = data.get("last_payment", "Never")
        result += f"👤 {name}\n   Status: {status}\n   Payments: {payments}\n   Last Payment: {last_payment}\n\n"
    
    return result


# ===================== MARKETING AGENT TOOLS =====================

@tool
def get_latest_music() -> str:
    """Gets the latest generated music file path.
    
    Returns:
        Path to the most recent music file
    """
    print("🔍 Finding latest music...")
    music_dir = "generated_music"
    
    if not os.path.exists(music_dir):
        return "❌ No music directory found. Generate music first."
    
    files = [f for f in os.listdir(music_dir) if f.endswith('.mp3') and '_sample_' not in f]
    
    if not files:
        return "❌ No music files found. Generate music first."
    
    files.sort(reverse=True)
    latest_file = os.path.join(music_dir, files[0])
    
    return f"✅ Latest music file: {latest_file}"

@tool
def create_music_sample(music_file: str, duration: int = 30) -> str:
    """Creates preview sample from a music file.
    
    Args:
        music_file: Path to the music file
        duration: Sample duration in seconds (default: 30)
    
    Returns:
        Path to the sample file
    """
    print("✂️ Creating sample...")
    
    if not os.path.exists(music_file):
        return f"❌ Music file not found: {music_file}"
    
    sample_path = music_file.replace('.mp3', f'_sample_{duration}s.mp3')
    
    # Simulate sample creation (in real app, use audio processing)
    shutil.copy(music_file, sample_path)
    
    return f"✅ Sample created: {sample_path} ({duration} seconds)"

@tool
def post_to_social_media(music_file: str, caption: str, platform: str = "all") -> str:
    """Posts music to social media platforms.
    
    Args:
        music_file: Path to the music file or sample
        caption: Engaging caption for the post
        platform: Target platform (default: "all" for all platforms)
    
    Returns:
        Confirmation of post with details
    """
    print("📱 Posting to social media...")
    
    if not os.path.exists(music_file):
        return f"❌ Music file not found: {music_file}"
    
    platforms = ["Twitter", "Instagram", "Facebook"] if platform == "all" else [platform]
    now = datetime.now()
    post_id = f"POST_{now.strftime('%Y%m%d%H%M%S')}"
    
    return f"✅ Posted to {', '.join(platforms)}!\n- File: {music_file}\n- Caption: {caption}\n- Post ID: {post_id}\n- Time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


# ===================== SIMPLIFIED MULTI-AGENT SYSTEM =====================

class SimplifiedAgent:
    """A simplified agent that uses LLM with tools"""
    
    def __init__(self, name: str, role: str, tools: list, llm):
        self.name = name
        self.role = role
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        
    def invoke(self, user_input: str) -> str:
        """Execute agent with ReAct-style reasoning"""
        
        tools_desc = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])
        
        prompt = f"""You are {self.name}, a {self.role}.

Your available tools:
{tools_desc}

User request: {user_input}

CRITICAL RULES:
1. You MUST use tools step-by-step
2. ONLY provide ONE action at a time
3. WAIT for the tool result before the next action
4. DO NOT imagine or predict tool results
5. ONLY say "Final Answer:" after you have ACTUALLY executed all tools

Respond in EXACTLY this format:
Thought: [what should I do next?]
Action: [tool name - ONLY ONE]
Action Input: [tool input as JSON - ONLY ONE]

Then STOP and WAIT for the Observation.

After receiving the Observation, you can continue with another Thought/Action or provide Final Answer.

NEVER provide multiple actions in one response!
NEVER say "Final Answer:" before executing the tools!"""

        max_iterations = 5
        conversation = []
        
        for i in range(max_iterations):
            print(f"\n--- {self.name} Iteration {i+1} ---")
            
            if conversation:
                full_prompt = prompt + "\n\n" + "\n".join(conversation)
            else:
                full_prompt = prompt
                
            response = self.llm.invoke(full_prompt).content
            
            print(f"\n{'─'*60}")
            print(f"📝 RAW RESPONSE (Iteration {i+1}):")
            print(f"{'─'*60}")
            print(response)
            print(f"{'─'*60}\n")
            
            # Check for final answer FIRST (before parsing actions)
            if "Final Answer:" in response:
                # But make sure there are no actions before it (agent trying to cheat)
                lines_before_final = response.split("Final Answer:")[0]
                if "Action:" in lines_before_final and "Action Input:" in lines_before_final:
                    print("⚠️ WARNING: LLM tried to include actions AND Final Answer in same response!")
                    print("   Extracting and executing the action first...")
                    # Continue to parse the action below
                else:
                    final = response.split("Final Answer:")[1].strip()
                    print(f"🏁 Final Answer found: {final[:100]}...")
                    return final
            
            # Parse action
            if "Action:" in response and "Action Input:" in response:
                print("🔍 Parsing action from response...")
                
                # Check if multiple actions (should not happen)
                action_count = response.count("Action:")
                if action_count > 1:
                    print(f"⚠️ WARNING: Multiple actions detected ({action_count})! Only executing the first one.")
                
                try:
                    lines = response.split('\n')
                    action_line = [l for l in lines if l.strip().startswith('Action:') and 'Action Input:' not in l][0]
                    action = action_line.split('Action:')[1].strip()
                    
                    input_line = [l for l in lines if 'Action Input:' in l][0]
                    action_input_str = input_line.split('Action Input:')[1].strip()
                    
                    # Parse JSON input
                    if action_input_str.strip() in ['{}', '']:
                        action_input = {}
                    else:
                        # Remove quotes if present
                        action_input_str = action_input_str.strip('"\'')
                        try:
                            action_input = json.loads(action_input_str)
                        except:
                            # If not JSON, treat as simple string for single-param tools
                            action_input = {"input": action_input_str}
                    
                    # Execute tool
                    if action in self.tools:
                        print(f"🔧 Executing: {action}")
                        print(f"   Input: {action_input}")
                        
                        try:
                            result = self.tools[action].invoke(action_input)
                            print(f"   ✅ Result: {result[:100]}...")
                        except Exception as tool_error:
                            result = f"❌ Tool Error: {str(tool_error)}"
                            print(f"   {result}")
                        
                        observation = f"Observation: {result}"
                        conversation.append(response)
                        conversation.append(observation)
                    else:
                        error_msg = f"❌ Error: Unknown tool '{action}'. Available tools: {list(self.tools.keys())}"
                        print(error_msg)
                        return error_msg
                        
                except Exception as e:
                    print(f"❌ Error parsing action: {e}")
                    print(f"   Response was: {response}")
                    return f"Error executing agent: {e}"
            else:
                # No clear action, return response as-is
                print(f"⚠️ No clear action found in response. Returning as-is.")
                print(f"   Full response: {response}")
                return response
        
        return "Max iterations reached. Please try again with a clearer request."


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
        
        print("✅ Multi-Agent System Initialized!")
        print("   🎵 Music Agent - Ready")
        print("   💳 Billing Agent - Ready")
        print("   📱 Marketing Agent - Ready")
    
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
            print(f"   ⚠️  Classification error: {e}")
            return "other"
    
    def _route_to_agent(self, user_input: str):
        """Smart routing with LLM + handles irrelevant questions"""
        
        # Classify the request
        category = self._classify_request(user_input)
        print(f"   🧠 Classification: {category}")
        
        # Handle irrelevant questions
        if category == "other":
            print(f"   ⚠️  Request outside system capabilities")
            
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
        print(f"   🎯 Routing → {agent.name}")
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
🎵 Music Generation - Create songs in different moods (happy, sad, energetic, etc.)
💳 Billing & Payments - Process payments, manage subscriptions, check customer status
📱 Social Media - Post music to Twitter, Instagram, Facebook

Your question seems to be outside these areas. Is there something related to music, billing, or marketing I can help you with?"""
            }
        
        print(f"📋 SUPERVISOR: Delegating to {agent.name}\n")
        
        try:
            # Execute with the selected agent
            output = agent.invoke(user_input)
            
            print(f"\n{'='*70}")
            print(f"✅ SUPERVISOR: Task completed by {agent.name}")
            print(f"{'='*70}\n")
            
            return {"output": output}
            
        except Exception as e:
            error_msg = f"Error in {agent.name}: {str(e)}"
            print(f"\n❌ {error_msg}\n")
            return {"output": error_msg}


def create_langchain_multiagent_system(api_key: str):
    """Factory function to create the multi-agent system"""
    return LangChainMultiAgentSystem(api_key)


__all__ = [
    'create_langchain_multiagent_system',
    'LangChainMultiAgentSystem',
    'load_database',
    'save_database'
]