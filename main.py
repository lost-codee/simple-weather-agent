import os
import json 
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from tools import get_weather
import re
from prompt_template import AGENT_PROMPT


# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def execute_tool(tool_name: str, tool_input: str) -> str:
    """Execute the specified tool with the given input."""
    
    if not tool_name or not tool_input:
        return "Error: Invalid tool action format"

    if tool_name == "get_weather":
        return get_weather(tool_input)
    
    return f"Error: Unknown tool '{tool_name}'"



def parse_agent_response(response: str) -> Dict[str, str]:
    """Parse the agent's response to extract thought, action, and action input."""
    lines = response.strip().split('\n')
    result = {}
    
    for line in lines:
        if line.startswith('Thought: '):
            result['thought'] = line[len('Thought: '):]
        elif line.startswith('Action: '):
            result['action'] = line[len('Action: '):]
        elif line.startswith('Action Input: '):
            result['action_input'] = line[len('Action Input: '):]
        elif line.startswith('Final Answer: '):
            result['final_answer'] = line[len('Final Answer: '):]
            
    return result


def run_agent(user_input: str) -> str:
    """Run the agent with the given question."""
    conversation = AGENT_PROMPT.format(question=user_input)
    max_steps = 3  # Prevent infinite loops
    step = 0

    while step < max_steps:   
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": conversation}],
            temperature=0,
        )

        content  = response.choices[0].message.content
        agent_response = parse_agent_response(content)

        # Check if we have a final answer
        if "final_answer" in agent_response:
            return agent_response["final_answer"]

        # Execute tool and add result to conversation
        if 'action' in agent_response and 'action_input' in agent_response:
            observation = execute_tool(agent_response['action'], agent_response['action_input'])
            conversation += f"\nObservation: {observation}\nThought:"
        else:
            return "Error: Invalid agent response format"

        # If not, continue the loop
        step += 1

    return "Error: Maximum number of steps reached"

def main():
    print("Weather Assistant (type 'quit' to exit)")
    print("Example questions:")
    print("- What's the weather in Tokyo?")
    print("- How's the weather in New York?\n")
    
    while True:
        userInput = input("Ask about weather (or 'quit' to exit): ")
        if userInput.lower() == 'quit':
            break
        try:
            answer = run_agent(userInput)
            print(f"\nAnswer: {answer}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
