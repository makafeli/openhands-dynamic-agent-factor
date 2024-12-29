"""
dynamic_agent_factory.py

A single-file demo showing how to build a meta-agent that auto-generates
new micro-agents in OpenHands, based on technology stack keywords.
"""

import os
import uuid
import importlib.util
from typing import Dict

# If you haven't installed OpenHands yet, you'll need:
#   pip install openhands
try:
    from openhands import MicroAgent
except ImportError:
    # Stub fallback if openhands isn't installed. Remove or replace in your environment.
    class MicroAgent:
        def __init__(self, name: str = "", description: str = "", inputs=None, outputs=None):
            self.name = name
            self.description = description
            self.inputs = inputs or []
            self.outputs = outputs or []
        def run(self, data: Dict):
            raise NotImplementedError("Stub class. Install openhands to use MicroAgent.")


# A mapping of keywords to unique agent class names
TRIGGER_MAP = {
    "python": "PythonAnalyzer",
    "react": "ReactAnalyzer",
    "node": "NodeAnalyzer"
}


def generate_agent_code(agent_class_name: str, tech_keyword: str) -> str:
    """
    Dynamically creates a string representing a MicroAgent subclass in Python.
    This code includes a basic `run()` method with placeholder logic.
    """
    # Capitalize the technology name for descriptive output
    capitalized = tech_keyword.capitalize()
    
    code_template = f'''\
from openhands import MicroAgent

class {agent_class_name}(MicroAgent):
    def __init__(self):
        super().__init__(
            name="{tech_keyword.lower()}_analyzer",
            description="Auto-generated agent for analyzing {capitalized} code/projects",
            inputs=["code_snippet"],
            outputs=["analysis_report"]
        )

    def run(self, data):
        code_snippet = data["code_snippet"]
        # Simple placeholder logic
        analysis = f"Automatically analyzing {capitalized} code: {{code_snippet[:50]}}..."
        return {{"analysis_report": analysis}}
'''
    return code_template


class DynamicAgentFactory(MicroAgent):
    """
    A meta-agent that listens for a technology trigger (like 'python', 'react', 'node')
    and then auto-generates a micro-agent for analyzing that technology.
    """

    def __init__(self):
        super().__init__(
            name="dynamic_agent_factory",
            description=(
                "Creates new micro-agents when triggered by specific technology keywords "
                "(e.g., python, react, node)."
            ),
            inputs=["technology_keyword"],
            outputs=["agent_class"]
        )

    def run(self, data: Dict):
        tech = data["technology_keyword"].lower()
        
        # Check if we have a matching trigger
        if tech in TRIGGER_MAP:
            agent_class_name = TRIGGER_MAP[tech]

            # 1) Generate the code string
            code_str = generate_agent_code(agent_class_name, tech)

            # 2) Write the code to a temporary file
            file_name = f"{agent_class_name.lower()}_{uuid.uuid4().hex}.py"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(code_str)

            # 3) Dynamically import that file as a module
            spec = importlib.util.spec_from_file_location(agent_class_name, file_name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 4) Extract the class from the module
            agent_cls = getattr(module, agent_class_name)
            
            # Optionally, remove the temp file after import:
            os.remove(file_name)

            # Return the newly created class
            return {"agent_class": agent_cls}

        else:
            return {
                "agent_class": None
            }


def main():
    """
    Demo usage: We create a DynamicAgentFactory, ask it for a 'python' agent,
    and then run that new agent with a sample code snippet.
    """
    factory = DynamicAgentFactory()

    # Example: user wants a Python-based analyzer agent
    output = factory.run({"technology_keyword": "python"})
    generated_agent_class = output["agent_class"]

    if generated_agent_class is None:
        print("No agent generated. No matching keyword found.")
        return

    # Instantiate the newly created micro-agent
    python_analyzer = generated_agent_class()

    # Run it with some sample code
    analysis_result = python_analyzer.run({"code_snippet": "def hello_world(): print('Hello World!')"})
    print("Analysis Report:", analysis_result["analysis_report"])


if __name__ == "__main__":
    main()
