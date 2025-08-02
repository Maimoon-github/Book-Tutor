from crewai import Agent
from tools.reading_tools import PreReadingActivator, InteractiveReader, PostReadingSynthesizer

class ReadingAgent(Agent):
    """
    Agent specialized in providing reading support through pre-reading,
    during-reading, and post-reading phases.

    This agent implements the "Guides Structured Learning" objective.
    """

    def __init__(self, llm):
        """Initialize the ReadingAgent with the necessary tools."""
        super().__init__(
            role="Reading Specialist",
            goal="Guide students through structured reading processes to maximize comprehension and knowledge acquisition.",
            backstory="I am an expert in reading strategies, comprehension, and educational scaffolding. "
                     "I help students prepare for new content, engage with text actively, and reflect "
                     "deeply after reading to solidify their understanding.",
            verbose=True,
            allow_delegation=True,
            llm=llm
        )

        # Add reading-specific tools
        self.tools = [
            PreReadingActivator(),
            InteractiveReader(),
            PostReadingSynthesizer()
        ]

    def generate_pre_reading_materials(self, chapter_info):
        """
        Generate pre-reading materials for a chapter.

        Args:
            chapter_info: Information about the chapter including title,
                         content, and learning outcomes

        Returns:
            Dict with pre-reading materials
        """
        # This would be implemented using the PreReadingActivator tool
        # The result might look like:
        result = {
            "questions": [
                "What do you already know about kindness in religious teachings?",
                "How does treating others with kindness affect society?"
            ],
            "vocabulary": [
                {"term": "virtue", "definition": "Behavior showing high moral standards"},
                {"term": "companions", "definition": "People you spend time with or travel with"}
            ],
            "concept_overview": "This chapter explores the kindness shown by the Holy Rasool "
                               "towards all beings, including humans, animals, and even plants. "
                               "It highlights how kindness is a fundamental value in Islam."
        }
        return result

    def provide_interactive_reading_support(self, chapter_content, section=None):
        """
        Provide interactive reading support for a chapter.

        Args:
            chapter_content: The content of the chapter
            section: Optional section indicator

        Returns:
            Dict with interactive reading elements
        """
        # This would be implemented using the InteractiveReader tool
        # Implementation details would go here
        pass

    def generate_post_reading_materials(self, chapter_info, reading_activity=None):
        """
        Generate post-reading materials for a chapter.

        Args:
            chapter_info: Information about the chapter
            reading_activity: Optional data about the student's reading activity

        Returns:
            Dict with post-reading materials
        """
        # This would be implemented using the PostReadingSynthesizer tool
        # Implementation details would go here
        pass
