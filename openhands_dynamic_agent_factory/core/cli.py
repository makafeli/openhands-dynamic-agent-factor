import sys
import argparse
from keyword_manager import KeywordManager

def main():
    manager = KeywordManager()

    if len(sys.argv) < 2:
        print("Please provide a command or input text.")
        return

    input_text = " ".join(sys.argv[1:])
    print(f"Input text: {input_text}")  # Debug logging

    # Automatically detect and handle keywords
    keyword = manager.detect_keyword(input_text)
    if keyword:
        print(manager.get_agent(keyword))
    else:
        print("No keyword detected. Here are the available commands:")
        print(manager.help())

if __name__ == "__main__":
    main()