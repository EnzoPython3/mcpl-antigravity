
import json

class N8nJsonAssemblerTool:
    """
    A tool to assemble the final n8n workflow JSON from a plan and
    generated code snippets.
    """

    def execute(self, plan: dict, code_snippets: dict) -> str:
        """
        Assembles the n8n workflow.

        Args:
            plan: The original structured plan from the Planner Agent.
            code_snippets: A dictionary mapping nodeId to the generated code.

        Returns:
            A JSON string of the final n8n workflow.
        """
        print("\n--- Assembling n8n Workflow JSON ---")

        # Create a deep copy of the plan's nodes to avoid modifying the original
        final_nodes = [dict(node) for node in plan.get("nodes", [])]
        
        # Inject the generated code into the appropriate nodes
        for node in final_nodes:
            node_id = node.get("nodeId")
            if node_id in code_snippets:
                # n8n's 'Code' node stores the JS in `parameters.functionCode`
                if "parameters" not in node:
                    node["parameters"] = {}
                node["parameters"]["functionCode"] = code_snippets[node_id]
                print(f"Injected code into node '{node_id}'.")

        # Construct the final workflow object in the n8n format
        n8n_workflow = {
            "name": plan.get("title", "Untitled Workflow"),
            "nodes": final_nodes,
            "connections": plan.get("connections", []),
            "active": True,
            "settings": {},
            "id": "1" # A placeholder ID
        }

        # For simplicity, we'll just return the JSON string.
        # A more robust implementation would save this to a file.
        return json.dumps(n8n_workflow, indent=2)

