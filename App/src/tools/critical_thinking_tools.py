from langchain.tools import BaseTool
from typing import Dict, Any, List, Union

class CriticalThinkingPromptGenerator(BaseTool):
    """
    Tool for generating critical thinking prompts, reflection questions,
    and scenarios to encourage deeper engagement.
    This corresponds to the CT_PROMPT tool in the system documentation.
    """

    name = "critical_thinking_prompt_generator"
    description = "Generate thought-provoking questions, scenarios, and reflection prompts to encourage critical thinking."

    def _run(
        self,
        chapter_info: Dict[str, Any],
        student_level: str = None
    ) -> Dict[str, Any]:
        """
        Run the tool to generate critical thinking prompts.

        Args:
            chapter_info: Information about the chapter
            student_level: Optional indicator of the student's level (e.g., "beginner", "intermediate", "advanced")

        Returns:
            Dict with critical thinking prompts
        """
        # Implementation would integrate with LLM to generate these prompts
        # This is a placeholder for the actual implementation

        # Adjust complexity based on student level
        complexity = "intermediate"
        if student_level:
            complexity = student_level

        # Generate different types of critical thinking prompts
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

    async def _arun(
        self,
        chapter_info: Dict[str, Any],
        student_level: str = None
    ) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(chapter_info, student_level)
