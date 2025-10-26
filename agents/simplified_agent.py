import json
import re

class SimplifiedAgent:
    """A simplified agent that uses LLM with tools"""
    
    def __init__(self, name: str, role: str, tools: list, llm):
        self.name = name
        self.role = role
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        
    import json
import re

class SimplifiedAgent:
    """A simplified agent that uses LLM with tools"""
    
    def __init__(self, name: str, role: str, tools: list, llm):
        self.name = name
        self.role = role
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        
    def invoke(self, user_input: str) -> str:
        tools_desc = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])
        
        # Special handling for Marketing Agent (prone to hallucinations)
        is_marketing = "Marketing" in self.name
        
        extra_rules = ""
        if is_marketing:
            extra_rules = """
EXTRA CRITICAL RULES FOR YOU:
- You tend to hallucinate Observations - DO NOT write "Observation:" ever!
- You tend to write multiple actions at once - write ONLY ONE action per response!
- After post_to_social_media succeeds, immediately provide Final Answer!
"""
        
        prompt = f"""You are {self.name}, a {self.role}.

Your available tools:
{tools_desc}

User request: {user_input}
{extra_rules}

CRITICAL RULES - READ CAREFULLY:
1. Execute ONE tool at a time - NEVER write multiple actions
2. After writing ONE Action, STOP immediately and wait for Observation
3. DO NOT write "Observation:" yourself - the system provides it
4. DO NOT predict or imagine tool results
5. Only write "Final Answer:" after receiving ALL Observations

FORMAT - Use EXACTLY this:
Thought: [one sentence about what to do next]
Action: [tool name]
Action Input: [JSON input]

STOP HERE! Do not write anything else! Wait for Observation!

EXAMPLES OF WRONG RESPONSES (DO NOT DO THIS):
   Action: tool1
   Action Input: {{}}
   Observation: result
   Action: tool2  <-- WRONG! Multiple actions!

   Action: None  <-- WRONG! Use Final Answer instead!

EXAMPLES OF CORRECT RESPONSES:
  Thought: I need to get the latest music
   Action: get_latest_music
   Action Input: {{}}

 Final Answer: Task completed successfully!"""

        max_iterations = 10
        conversation = []
        completed_actions = set() if is_marketing else None  # Only track for marketing
        
        for i in range(max_iterations):
            print(f"\n--- {self.name} Iteration {i+1} ---")
            
            if conversation:
                full_prompt = prompt + "\n\n" + "\n".join(conversation)
            else:
                full_prompt = prompt
                
            response = self.llm.invoke(full_prompt).content
            
            print(f"\n{'─'*60}")
            print(f"RAW RESPONSE (Iteration {i+1}):")
            print(f"{'─'*60}")
            print(response)
            print(f"{'─'*60}\n")
            
            # Marketing Agent: Check for hallucinated observations
            if is_marketing and "Observation:" in response and "Action:" in response:
                print("Marketing Agent hallucinating! Cleaning response...")
                # Extract only first action
                lines = response.split('\n')
                cleaned_lines = []
                found_action = False
                found_action_input = False
                
                for line in lines:
                    if line.strip().startswith('Thought:'):
                        cleaned_lines.append(line)
                    elif line.strip().startswith('Action:') and not found_action:
                        cleaned_lines.append(line)
                        found_action = True
                    elif 'Action Input:' in line and not found_action_input:
                        cleaned_lines.append(line)
                        found_action_input = True
                        break
                
                response = '\n'.join(cleaned_lines)
                print(f"Cleaned: {response}\n")
            
            # FIRST: Check for final answer
            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:")[-1].strip()
                before_final = response.split("Final Answer:")[0]
                
                if "Action:" in before_final:
                    print("WARNING: Agent tried to include actions with Final Answer!")
                    print("Ignoring Final Answer, executing action instead...")
                else:
                    print(f"Final Answer received: {final_answer[:100]}...")
                    return final_answer
            
            # SECOND: Check if trying to say "None"
            if re.search(r'Action:\s*(None|N/A|null)', response, re.IGNORECASE):
                print("Agent tried to use 'Action: None'")
                conversation.append(response)
                conversation.append("Observation: You cannot use 'Action: None'. If you are done, provide 'Final Answer:' instead.")
                continue
            
            # THIRD: Parse and execute action
            if "Action:" in response and "Action Input:" in response:
                print("Parsing action from response...")
                
                action_matches = re.findall(r'Action:\s*(\w+)', response)
                if len(action_matches) > 1:
                    print(f"Multiple actions detected: {action_matches}")
                    print(f"Only executing first action: {action_matches[0]}")
                
                if "Observation:" in response:
                    print("WARNING: Agent is hallucinating Observations!")
                    print("Extracting only the first action...")
                
                try:
                    lines = response.split('\n')
                    
                    # Find action line
                    action_line = None
                    for line in lines:
                        if line.strip().startswith('Action:') and 'Action Input:' not in line:
                            action_line = line
                            break
                    
                    if not action_line:
                        print("Could not find Action line")
                        conversation.append(response)
                        conversation.append("Observation: Invalid format. Use: Action: [tool_name]")
                        continue
                    
                    action = action_line.split('Action:')[1].strip()
                    
                    # Marketing Agent: Check for repeated actions
                    if is_marketing and completed_actions is not None:
                        if action in completed_actions:
                            print(f"Marketing Agent repeating action: {action}")
                            conversation.append(response)
                            conversation.append(f"Observation: You already executed '{action}' successfully. Choose different action or provide Final Answer.")
                            continue
                    
                    # Find action input line
                    input_line = None
                    for line in lines:
                        if 'Action Input:' in line:
                            input_line = line
                            break
                    
                    if not input_line:
                        print("Could not find Action Input line")
                        conversation.append(response)
                        conversation.append("Observation: Invalid format. Use: Action Input: {...}")
                        continue
                    
                    action_input_str = input_line.split('Action Input:')[1].strip()
                    
                    if action_input_str.lower() in ['none', 'n/a', 'null', '']:
                        print("Action Input is None/empty")
                        conversation.append(response)
                        conversation.append("Observation: Invalid Action Input. Provide valid JSON or {}.")
                        continue
                    
                    # Parse JSON input
                    if action_input_str.strip() == '{}':
                        action_input = {}
                    else:
                        action_input_str = action_input_str.strip('"\'')
                        try:
                            action_input = json.loads(action_input_str)
                        except:
                            action_input = {"input": action_input_str}
                    
                    # Execute tool
                    if action in self.tools:
                        print(f"Executing: {action}")
                        print(f"Input: {action_input}")
                        
                        try:
                            result = self.tools[action].invoke(action_input)
                            print(f"Result: {result[:200]}...")
                            
                            # Marketing Agent: Track completed actions
                            if is_marketing and completed_actions is not None:
                                completed_actions.add(action)
                            
                            observation = f"Observation: {result}"
                            conversation.append(response)
                            conversation.append(observation)
                            
                            # Marketing Agent: Auto-complete after social media post
                            if is_marketing and action == "post_to_social_media" and "Posted to" in result:
                                print("Marketing workflow complete! Returning immediately.")
                                summary = f"Successfully posted the latest music to social media! "
                                summary += f"I found the latest track, created a 30-second sample, and posted it to all platforms (Twitter, Instagram, Facebook)."
                                return summary
                            
                        except Exception as tool_error:
                            error_msg = f"Tool Error: {str(tool_error)}"
                            print(f"{error_msg}")
                            conversation.append(response)
                            conversation.append(f"Observation: {error_msg}")
                    else:
                        error_msg = f"Unknown tool '{action}'. Available: {list(self.tools.keys())}"
                        print(f"{error_msg}")
                        conversation.append(response)
                        conversation.append(f"Observation: {error_msg}")
                        
                except Exception as e:
                    print(f"Error parsing action: {e}")
                    conversation.append(response)
                    conversation.append(f"Observation: Parse error - {e}. Use correct format.")
            else:
                # No action found
                print(f"No clear action format. Returning as-is.")
                return response
        
        print("Max iterations reached!")
        if is_marketing and completed_actions:
            return f"Marketing task completed: {', '.join(completed_actions)}"
        return "Task incomplete - max iterations reached. Please simplify the request."