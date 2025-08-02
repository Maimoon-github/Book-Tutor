from crewai import Crew, Task, Agent
from typing import Dict, List, Any
import os
from core.ollama_llm import OllamaLLM

class BookTutor:
    """
    Main BookTutor class that orchestrates the educational AI agents.

    This class serves as the central coordinator for all tutor functionality:
    - Loading and managing curriculum content
    - Creating and orchestrating specialized AI agents
    - Managing student sessions and progress tracking
    - Processing requests and generating responses
    """

    def __init__(self):
        """Initialize the BookTutor with default settings and load the curriculum."""
        # Current state tracking
        self.current_chapter = None
        self.current_phase = None  # pre-reading, during-reading, post-reading
        self.student_progress = {}

        # Initialize the LLM using Ollama local model
        self.llm = OllamaLLM.from_env()

        # Load curriculum
        self.curriculum = self._load_curriculum()

        # Initialize agents
        self.agents = self._initialize_agents()

        # Create the agent crew
        self.crew = self._create_crew()

    def _load_curriculum(self):
        """Load curriculum content from files."""
        # This will be implemented to load chapter content and metadata
        curriculum = {
            "chapters": {
                1: {
                    "title": "Kindness of the Holy Rasool",
                    "content_path": "../Curriculum/chapter_1.txt",
                    "learning_outcomes": [
                        "use pre-reading strategies to predict content",
                        "apply critical thinking with intensive reading strategies",
                        "use critical thinking to respond to text",
                        "pronounce and practice diphthongs",
                        "analyze and use conjunctions",
                        "demonstrate use of prepositions",
                        "use context to infer missing words",
                        "identify and recognize the function of possessive pronouns",
                        "demonstrate the use of joining words"
                    ]
                },
                2: {
                    "title": "Chapter 2",  # Will be updated with actual title
                    "content_path": "../Curriculum/chapter_2.txt",
                    "learning_outcomes": [
                        "use pre-reading strategies",
                        "apply while-reading strategies",
                        "use post reading strategies",
                        "pronounce and practice words with silent letters",
                        "articulate, practice and syllabify words",
                        "classify and use naming, action and describing words",
                        "recall and demonstrate use of nouns",
                        "recall and practice the use of articles",
                        "write multi-syllable words with correct spellings"
                    ]
                },
                3: {
                    "title": "Chapter 3",  # Will be updated with actual title
                    "content_path": "../Curriculum/chapter_3.txt",
                    "learning_outcomes": [
                        "use pre-reading strategies",
                        "apply while-reading strategies",
                        "use post reading strategies",
                        "classify and use adjectives",
                        "classify words that begin with vowel sounds",
                        "use appropriate expression",
                        "change the number of regular and irregular nouns",
                        "recognize meaning of common adjectives and verbs",
                        "analyze and use conjunctions",
                        "write a paragraph to describe/show sequence"
                    ]
                }
            }
        }
        return curriculum

    def _initialize_agents(self):
        """Initialize the specialized educational agents."""
        # Import agent classes
        from agents.reading_agent import ReadingAgent
        from agents.assessment_agent import AssessmentAgent
        from agents.critical_thinking_agent import CriticalThinkingAgent
        from agents.teacher_agent import TeacherAgent
        from agents.curriculum_agent import CurriculumAgent

        # Create agent instances
        agents = {
            "reading_agent": ReadingAgent(llm=self.llm),
            "assessment_agent": AssessmentAgent(llm=self.llm),
            "critical_thinking_agent": CriticalThinkingAgent(llm=self.llm),
            "teacher_agent": TeacherAgent(llm=self.llm),
            "curriculum_agent": CurriculumAgent(llm=self.llm)
        }

        return agents

    def _create_crew(self):
        """Create the CrewAI crew with all agents."""
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[],  # Tasks will be created dynamically based on context
            verbose=True
        )
        return crew

    def generate_pre_reading_content(self, chapter_id):
        """
        Generate pre-reading content for a specific chapter.

        Args:
            chapter_id: The ID of the chapter

        Returns:
            Dict containing pre-reading questions, vocabulary, and concept overview
        """
        self.current_chapter = chapter_id
        self.current_phase = "pre-reading"

        # Create a task for the reading agent
        task = Task(
            description=f"Generate pre-reading materials for Chapter {chapter_id}: {self.curriculum['chapters'][chapter_id]['title']}",
            expected_output="JSON with pre-reading questions, vocabulary list, and concept overview",
            agent=self.agents["reading_agent"]
        )

        # Execute the task
        result = task.execute()

        # Process and return the results
        return result

    def generate_during_reading_content(self, chapter_id, section=None):
        """
        Generate during-reading content for a specific chapter/section.

        Args:
            chapter_id: The ID of the chapter
            section: Optional section identifier

        Returns:
            Dict containing interactive reading content with definitions, checks, etc.
        """
        self.current_chapter = chapter_id
        self.current_phase = "during-reading"

        # Create a task for the reading agent
        task = Task(
            description=f"Generate during-reading materials for Chapter {chapter_id}: {self.curriculum['chapters'][chapter_id]['title']}",
            expected_output="JSON with interactive reading content including definitions, comprehension checks",
            agent=self.agents["reading_agent"]
        )

        # Execute the task
        result = task.execute()

        # Process and return the results
        return result

    def generate_post_reading_content(self, chapter_id):
        """
        Generate post-reading content for a specific chapter.

        Args:
            chapter_id: The ID of the chapter

        Returns:
            Dict containing post-reading summary prompts, discussion questions, etc.
        """
        self.current_chapter = chapter_id
        self.current_phase = "post-reading"

        # Create a task for the reading agent
        task = Task(
            description=f"Generate post-reading materials for Chapter {chapter_id}: {self.curriculum['chapters'][chapter_id]['title']}",
            expected_output="JSON with post-reading summary prompts, discussion questions",
            agent=self.agents["reading_agent"]
        )

        # Execute the task
        result = task.execute()

        # Process and return the results
        return result

    def generate_assessment(self, chapter_id, difficulty=None, question_types=None):
        """
        Generate assessment questions for a specific chapter.

        Args:
            chapter_id: The ID of the chapter
            difficulty: Optional difficulty level
            question_types: Optional list of question types

        Returns:
            Dict containing assessment questions
        """
        # Create a task for the assessment agent
        task = Task(
            description=f"Generate assessment for Chapter {chapter_id}: {self.curriculum['chapters'][chapter_id]['title']}",
            expected_output="JSON with assessment questions",
            agent=self.agents["assessment_agent"]
        )

        # Execute the task
        result = task.execute()

        # Process and return the results
        return result

    def generate_critical_thinking_prompts(self, chapter_id):
        """
        Generate critical thinking prompts for a specific chapter.

        Args:
            chapter_id: The ID of the chapter

        Returns:
            Dict containing critical thinking prompts
        """
        # Create a task for the critical thinking agent
        task = Task(
            description=f"Generate critical thinking prompts for Chapter {chapter_id}: {self.curriculum['chapters'][chapter_id]['title']}",
            expected_output="JSON with critical thinking prompts",
            agent=self.agents["critical_thinking_agent"]
        )

        # Execute the task
        result = task.execute()

        # Process and return the results
        return result

    def update_student_progress(self, chapter_id, phase, activity, result):
        """
        Update the student's progress tracking.

        Args:
            chapter_id: The ID of the chapter
            phase: The learning phase (pre-reading, during-reading, post-reading)
            activity: The specific activity within the phase
            result: The result/score/completion of the activity
        """
        if chapter_id not in self.student_progress:
            self.student_progress[chapter_id] = {}

        if phase not in self.student_progress[chapter_id]:
            self.student_progress[chapter_id][phase] = {}

        self.student_progress[chapter_id][phase][activity] = result

        # Use the teacher agent to analyze progress and provide recommendations
        task = Task(
            description=f"Analyze student progress for Chapter {chapter_id}, Phase {phase}, Activity {activity}",
            expected_output="JSON with progress analysis and recommendations",
            agent=self.agents["teacher_agent"]
        )

        result = task.execute()
        return result
