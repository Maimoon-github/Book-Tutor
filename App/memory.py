import json
from typing import List, Dict, Any
from pathlib import Path

class Memory:
    """
    A class to handle the agent's memory, persisting it to a JSON file.
    """
    def __init__(self, memory_file: str = "memory.json"):
        """
        Initializes the Memory class.

        Args:
            memory_file: The path to the JSON file where memory is stored.
        """
        self.memory_file = Path(memory_file)
        self.history = self._load_memory()

    def _load_memory(self) -> List[Dict[str, Any]]:
        """Loads the conversation history from the JSON file."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_memory(self):
        """Saves the conversation history to the JSON file."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4)

    def add(self, role: str, content: str):
        """
        Adds a new entry to the memory.

        Args:
            role: The role of the speaker (e.g., 'user', 'agent', 'system').
            content: The text content of the entry.
        """
        if not isinstance(role, str) or not isinstance(content, str):
            print("Error: Role and content must be strings.")
            return

        self.history.append({"role": role, "content": content})
        self._save_memory()

    def retrieve(self, last_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the last k entries from the history.

        Args:
            last_k: The number of recent entries to retrieve.

        Returns:
            A list of the most recent history entries.
        """
        return self.history[-last_k:]

    def clear(self):
        """Clears the entire conversation history."""
        self.history = []
        self._save_memory()

if __name__ == '__main__':
    # Example usage:
    memory = Memory(memory_file="test_memory.json")
    memory.clear() # Start with a clean slate for the test

    print("Initial Memory:", memory.retrieve())

    # Add some interactions
    memory.add("user", "Hello, who are you?")
    memory.add("agent", "I am an AI assistant.")
    memory.add("user", "What can you do?")

    print("\nUpdated Memory:", memory.retrieve())

    # Add another interaction
    memory.add("agent", "I can help you with a variety of tasks. How can I assist you today?")

    print("\nFinal Memory (last 3):", memory.retrieve(last_k=3))

    # Clean up the test file
    import os
    os.remove("test_memory.json")
