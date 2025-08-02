from crewai import Agent
from tools.critical_thinking_tools import CriticalThinkingPromptGenerator

class CriticalThinkingAgent(Agent):
    """
    Agent specialized in generating thought-provoking questions and scenarios
    to encourage critical thinking and deeper engagement.

    This agent implements the "Encourages Critical Thinking" objective.
    """

    def __init__(self, llm):
        """Initialize the CriticalThinkingAgent with the necessary tools."""
        super().__init__(
            role="Critical Thinking Facilitator",
            goal="Encourage students to think deeply, analyze information critically, and develop higher-order thinking skills.",
            backstory="I am an expert in fostering critical thinking skills through "
                     "thoughtful questioning and scenario design. I help students move "
                     "beyond basic comprehension to analysis, synthesis, and evaluation.",
            verbose=True,
            allow_delegation=True,
            llm=llm
        )

        # Add critical thinking-specific tools
        self.tools = [
            CriticalThinkingPromptGenerator()
        ]

    def generate_critical_thinking_prompts(self, chapter_info, student_level=None):
        """
        Generate critical thinking prompts for a chapter.

        Args:
            chapter_info: Information about the chapter
            student_level: Optional indicator of the student's level

        Returns:
            Dict with critical thinking prompts
        """
        # This would be implemented using the CriticalThinkingPromptGenerator tool
        # Example implementation:
        result = {
            "reflection_questions": [
                "How might our world be different if everyone followed the Holy Rasool's teaching about kindness to all creatures?",
                "Why do you think the Holy Rasool emphasized kindness not just to humans but to animals as well?",
                "In what ways can showing kindness to animals reflect our character as human beings?"
            ],
            "scenarios": [
                {
                    "scenario": "You notice a classmate who keeps a pet bird in a very small cage where it can barely move. The bird looks unhealthy. What would you do based on the teachings from this chapter?",
                    "questions": [
                        "What values from the chapter would guide your actions?",
                        "How could you approach this situation with kindness to both the bird and your classmate?"
                    ]
                }
            ],
            "connections": [
                "Connect the Holy Rasool's teachings on kindness to animals with modern animal welfare movements. What similarities and differences do you see?",
                "Think about a time when you showed kindness to an animal. How did it make you feel? How might the animal have felt?"
            ]
        }
        return result

    def generate_socratic_dialogue(self, topic, initial_response=None):
        """
        Generate a Socratic dialogue to guide deeper inquiry on a topic.

        Args:
            topic: The topic to explore
            initial_response: Optional initial student response

        Returns:
            Dict with Socratic dialogue prompts
        """
        # Implementation details would go here
        pass
