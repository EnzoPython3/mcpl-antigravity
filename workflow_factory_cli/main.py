
from dotenv import load_dotenv
load_dotenv()

import argparse
import asyncio
import json
import os
from llms import GeminiLlm, ClaudeLlm
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from tools.n8n_assembler import N8nJsonAssemblerTool
from tools.code_writer import CodeWriterTool

async def run_workflow(prompt: str):
    """
    This is the main co-routine that will orchestrate the agent workflow.
    """
    print(f"Received goal: {prompt}\n")

    # 1. Instantiate the LLMs for their designated roles
    try:
        planner_llm = GeminiLlm(model="gemini-3-pro")
        executor_llm = ClaudeLlm(model="anthropic/claude-3-opus")
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("Please create a '.env' file in the 'workflow_factory_cli' directory and add your API keys.")
        print("You can use 'workflow_factory_cli/.env.example' as a template.")
        return

    # 2. Instantiate and run the Planner Agent
    print("--- Invoking Planner Agent ---")
    planner_agent = PlannerAgent(llm=planner_llm)
    automation_plan = await planner_agent.generate_plan(prompt)

    if not automation_plan:
        print("\nWorkflow generation failed because the planner did not produce a valid plan.")
        return

    print("\n--- Planner Agent finished. ---")
    
    # 3. Instantiate and run the Executor Agent
    print("\n--- Invoking Executor Agent ---")
    executor_agent = ExecutorAgent(llm=executor_llm)
    generated_code = await executor_agent.execute_plan(automation_plan)

    if not generated_code:
        print("\nWorkflow generation failed because the executor did not produce any code.")
        return
        
    print("\n--- Executor Agent finished. ---")

    # 4. Assemble and save the final workflow
    print("\n--- Assembling Final Workflow ---")
    assembler_tool = N8nJsonAssemblerTool()
    final_workflow_json = assembler_tool.execute(automation_plan, generated_code)

    print("\nFinal n8n Workflow JSON:")
    print(final_workflow_json)

    # Save the workflow to a file
    output_dir = "workflows"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "workflow.json")
    
    with open(output_path, 'w') as f:
        f.write(final_workflow_json)
        
    print(f"\nSuccessfully saved workflow to '{output_path}'")

    print("\nOrchestrator finished.")

def main():
    """
    Entry point for the Workflow Factory CLI.
    """
    parser = argparse.ArgumentParser(
        description="A CLI tool to build automation workflows using AI agents."
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The high-level goal for the automation workflow.",
    )
    # TODO: Add arguments for model selection, output file, etc.
    
    args = parser.parse_args()

    print("--- Workflow Factory CLI Initializing ---")
    try:
        asyncio.run(run_workflow(args.prompt))
    except KeyboardInterrupt:
        print("\nWorkflow generation cancelled by user.")
    finally:
        print("--- Workflow Factory CLI Shutting Down ---")

if __name__ == "__main__":
    main()
