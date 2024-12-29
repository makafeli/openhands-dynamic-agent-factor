"""
Basic example of using the dynamic agent factory.
"""

from openhands_dynamic_agent_factory import DynamicAgentFactoryLLM

def main():
    """Example usage of the DynamicAgentFactoryLLM."""
    try:
        # Create the factory
        factory = DynamicAgentFactoryLLM()
        
        # Example: Generate a Python analyzer with options
        result = factory.run({
            "technology_keyword": "python",
            "options": {
                "analysis_type": "security",
                "max_code_length": 5000
            }
        })

        if result["agent_class"] is None:
            print("Agent generation failed:", result["generation_info"].get("error"))
            return

        # Create an instance of the generated agent
        agent = result["agent_class"]()
        
        # Example code analysis
        sample_code = """
        def process_data(user_input):
            result = eval(user_input)  # Security risk!
            return result
        """
        
        analysis = agent.run({
            "code_snippet": sample_code,
            "analysis_type": "security"
        })
        
        print("\nGeneration Info:", result["generation_info"])
        print("\nAnalysis Results:", analysis)

    except Exception as e:
        print(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()