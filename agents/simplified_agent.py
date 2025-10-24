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
        
        prompt = f"""You are {self.name}, a {self.role}.

Your available tools:
{tools_desc}

User request: {user_input}

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

        max_iterations = 10  # Increased for complex workflows
        conversation = []
        
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
            
            # FIRST: Check for final answer
            if "Final Answer:" in response:
                # Extract only the part after "Final Answer:"
                final_answer = response.split("Final Answer:")[-1].strip()
                
                # Check if there are actions BEFORE the final answer (hallucination)
                before_final = response.split("Final Answer:")[0]
                if "Action:" in before_final:
                    print("WARNING: Agent tried to include actions with Final Answer!")
                    print("Ignoring Final Answer, executing action instead...")
                    # Continue to parse action below
                else:
                    print(f"Final Answer received: {final_answer[:100]}...")
                    return final_answer
            
            # SECOND: Check if trying to say "None"
            if re.search(r'Action:\s*(None|N/A|null)', response, re.IGNORECASE):
                print("Agent tried to use 'Action: None'")
                print("Prompting agent to provide Final Answer...")
                conversation.append(response)
                conversation.append("Observation: You cannot use 'Action: None'. If you are done, provide 'Final Answer:' instead.")
                continue
            
            # THIRD: Parse and execute action
            if "Action:" in response and "Action Input:" in response:
                print("Parsing action from response...")
                
                # Check for multiple actions (common mistake)
                action_matches = re.findall(r'Action:\s*(\w+)', response)
                if len(action_matches) > 1:
                    print(f"Multiple actions detected: {action_matches}")
                    print(f"Only executing first action: {action_matches[0]}")
                
                # Check if agent wrote "Observation:" (hallucinating)
                if "Observation:" in response:
                    print("WARNING: Agent is hallucinating Observations!")
                    print("Extracting only the first action...")
                
                try:
                    # Extract ONLY the first action
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
                    
                    # Skip None values
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
                            
                            observation = f"Observation: {result}"
                            conversation.append(response)
                            conversation.append(observation)
                            
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
                # No action found - treat as final response
                print(f"No clear action format. Returning as-is.")
                return response
        
        print("Max iterations reached!")
        return "Task incomplete - max iterations reached. Please simplify the request."