
import json
from llms import BaseLlm
from tools.web_search import WebSearchTool

class PlannerAgent:
    """
    The Planner Agent is responsible for creating a structured plan 
    for an automation workflow.
    """

    def __init__(self, llm: BaseLlm):
        self.llm = llm
        self.search_tool = WebSearchTool()

    async def generate_plan(self, goal: str) -> dict:
        """
        Generates a structured automation plan based on a user goal.

        Args:
            goal: The high-level goal from the user.

        Returns:
            A dictionary representing the structured JSON plan.
        """
        print("--- Planner Agent ---")
        
        # Step 1: Use the WebSearchTool to research the goal.
        # This simulates the agent "thinking" about what it needs to know.
        print("Researching necessary components...")
        search_query_1 = f"n8n nodes for {goal}"
        search_query_2 = "Hacker News API" # A common example
        
        # Execute searches (currently mocked)
        search_results_1 = await self.search_tool.execute(search_query_1)
        search_results_2 = await self.search_tool.execute(search_query_2)
        
        research_summary = f"Research Summary:\n{search_results_1}\n{search_results_2}"
        print(f"Research complete.\n{research_summary}")

        # Step 2: Construct the prompt for the planner LLM.
        prompt = self._construct_prompt(goal, research_summary)

        # Step 3: Call the LLM to generate the plan.
        print("Generating plan using the planner LLM...")
        
        # The planner's response is expected to be a structured JSON plan
        # We are still using the mocked LLM which returns a valid JSON string.
        plan_json_str = await self.llm.generate_content(prompt)

        # Step 4: Validate and parse the plan.
        try:
            plan = json.loads(plan_json_str)
            print("Successfully parsed the plan.")
            return plan
        except json.JSONDecodeError:
            print("Error: The planner LLM did not return a valid JSON plan.")
            # In a real implementation, you might want to add a retry loop here.
            return None

    def _construct_prompt(self, goal: str, research: str) -> str:
        """Constructs the detailed prompt for the planner LLM."""
        
        # This is a basic prompt template. A more advanced version could be loaded from a file.
        return f"""

You are an expert automation architect. Your task is to create a detailed, structured JSON plan for an automation workflow based on a user's goal.

**User Goal:**
{goal}

**Research Findings:**
Based on my research, here is some relevant information about the tools and APIs available:
{research}

**Instructions:**
1.  Analyze the user's goal and the research findings.
2.  Define the necessary steps as a series of 'nodes' (e.g., trigger, HTTP request, code execution, sending a message).
3.  For any step that requires custom code logic, create a detailed, natural-language prompt for another AI (a code-generation expert) to write that code.
4.  Output a JSON object that strictly follows this structure:
    {{
      "title": "A descriptive title for the workflow",
      "platform": "n8n" or "GoogleAppsScript",
      "trigger": {{ "type": "node_type", "description": "..." }},
      "nodes": [ {{ "nodeId": "...", "type": "...", "description": "...", "parameters": {{ ... }} }} ],
      "connections": [ {{ "from": "nodeId", "to": "nodeId" }} ],
      "customCode": [ {{ "nodeId": "...", "language": "javascript", "prompt": "A detailed prompt for the coding AI." }} ]
    }}
5.  Ensure the `nodeId`s are unique and consistent between the `nodes`, `connections`, and `customCode` sections.
6.  Do not write the actual code, only the prompts for the coding AI.
7.  Respond ONLY with the raw JSON object. Do not include any other text or formatting.
"""
