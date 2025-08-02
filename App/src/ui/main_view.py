import streamlit as st
import json
from typing import Dict, Any

def setup_main_view(book_tutor):
    """
    Set up the main view for the tutor interface.

    Args:
        book_tutor: BookTutor instance
    """
    # Get the current selections from session state
    chapter_id = st.session_state.get("selected_chapter", 1)
    learning_phase = st.session_state.get("selected_phase", "pre_reading")

    # Dispatch to the appropriate view based on learning phase
    if learning_phase == "pre_reading":
        show_pre_reading_view(book_tutor, chapter_id)
    elif learning_phase == "during_reading":
        show_during_reading_view(book_tutor, chapter_id)
    elif learning_phase == "post_reading":
        show_post_reading_view(book_tutor, chapter_id)
    elif learning_phase == "assessment":
        show_assessment_view(book_tutor, chapter_id)
    elif learning_phase == "critical_thinking":
        show_critical_thinking_view(book_tutor, chapter_id)


def show_pre_reading_view(book_tutor, chapter_id):
    """
    Show pre-reading phase view.

    Args:
        book_tutor: BookTutor instance
        chapter_id: ID of the current chapter
    """
    st.header("Pre-Reading Activities")

    # This would normally call book_tutor.generate_pre_reading_content(chapter_id)
    # For demonstration, we'll use placeholder data
    pre_reading_content = {
        "questions": [
            "What do you already know about kindness in religious teachings?",
            "How does treating others with kindness affect society?"
        ],
        "vocabulary": [
            {"term": "virtue", "definition": "Behavior showing high moral standards"},
            {"term": "companions", "definition": "People you spend time with or travel with"},
            {"term": "discrimination", "definition": "Treating someone differently based on their characteristics"},
            {"term": "affectionate", "definition": "Showing care and fondness for someone/something"}
        ],
        "concept_overview": "This chapter explores the kindness shown by the Holy Rasool towards all beings, including humans, animals, and even plants. It highlights how kindness is a fundamental value in Islam."
    }

    # Display the concept overview
    st.subheader("Chapter Overview")
    st.write(pre_reading_content["concept_overview"])

    # Display activating questions
    st.subheader("Thinking Questions")
    for i, question in enumerate(pre_reading_content["questions"]):
        st.text_input(f"Question {i+1}", value=question, disabled=True)
        user_answer = st.text_area(f"Your thoughts on question {i+1}:", key=f"pre_q_{i}")
        if user_answer:
            # In a real implementation, this would send the answer to the AI for feedback
            st.success("✓ Response saved")

    # Display vocabulary section
    st.subheader("Key Vocabulary")
    cols = st.columns(2)
    for i, vocab in enumerate(pre_reading_content["vocabulary"]):
        with cols[i % 2]:
            with st.expander(vocab["term"]):
                st.write(vocab["definition"])

    st.divider()

    # Button to indicate readiness to proceed to reading
    if st.button("I'm Ready to Start Reading"):
        st.session_state.selected_phase = "during_reading"
        st.rerun()


def show_during_reading_view(book_tutor, chapter_id):
    """
    Show during-reading phase view.

    Args:
        book_tutor: BookTutor instance
        chapter_id: ID of the current chapter
    """
    st.header("Reading")

    # This would normally get the chapter content from the curriculum
    # For demonstration, we'll use placeholder data
    chapter_content = """The life of our kind Rasool is the role-model for all humanity till the Day of Judgment. Patience and kindness were the greatest virtues of our Holy Rasool. He repeatedly advised his companions to be kind to all the lives around them, without any discrimination. The Holy Rasool was kind and affectionate not only to human beings but also to all creatures of the universe. For this very reason Allah Almighty was pleased to bestow upon him the title of 'Benefactor of all the worlds.'

Once Holy Rasool told his companions, "Allah Almighty will not be kind to him who is not kind to others." Whenever our kind Rasool used to come across any animal which was over-burdened or ill fed he would speak mildly to the owner and say "Fear Allah regarding these dumb animals. Ride them when they are in good condition and feed them when they are in good condition." (Abu Dawood-2548)

Once the Holy Rasool was traveling with his companions. During their journey when they decided to have some rest under the shade of date palm trees, Rasool entered in the bushes nearby which belonged to a man from Ansaar. Suddenly a camel came towards him weeping tenderly with its eyes welling with tears. When the camel reached Rasool it began to groan and its eyes flowed with tears. Holy Rasool patted on its hump and the base of its head until the camel quieted down. Then, He asked "who is the owner of this camel?" a young man came forward and said "it is mine, O Messenger of Allah." Rasool said "Do you not fear Allah with regard to this creature which He has placed in your possession? It has complained to me that you starve it and put it to extreme work." (Abu Dawood-2549) The young man understood the words of Rasool and then the Holy Rasool and his companions continued their journey."""

    # Processed content with annotations, definitions, and comprehension checks
    processed_content = [
        {
            "paragraph": "The life of our kind Rasool is the role-model for all humanity till the Day of Judgment. Patience and kindness were the greatest virtues of our Holy Rasool. He repeatedly advised his companions to be kind to all the lives around them, without any discrimination. The Holy Rasool was kind and affectionate not only to human beings but also to all creatures of the universe. For this very reason Allah Almighty was pleased to bestow upon him the title of 'Benefactor of all the worlds.'",
            "definitions": {
                "role-model": "A person looked to by others as an example to be imitated",
                "virtues": "Good moral qualities or behaviors",
                "discrimination": "Unfair treatment based on prejudice",
                "bestow": "To give or present something",
                "benefactor": "A person who helps others"
            },
            "comprehension_check": {
                "question": "What title did Allah Almighty bestow upon the Holy Rasool?",
                "answer": "Benefactor of all the worlds"
            }
        },
        {
            "paragraph": "Once Holy Rasool told his companions, \"Allah Almighty will not be kind to him who is not kind to others.\" Whenever our kind Rasool used to come across any animal which was over-burdened or ill fed he would speak mildly to the owner and say \"Fear Allah regarding these dumb animals. Ride them when they are in good condition and feed them when they are in good condition.\" (Abu Dawood-2548)",
            "definitions": {
                "over-burdened": "Given too much to carry or too much work",
                "ill fed": "Not given enough food",
                "mildly": "In a gentle manner",
                "dumb animals": "Animals that cannot speak"
            },
            "comprehension_check": {
                "question": "What did the Holy Rasool advise owners about their animals?",
                "answer": "To ride them and feed them when they are in good condition"
            }
        },
        {
            "paragraph": "Once the Holy Rasool was traveling with his companions. During their journey when they decided to have some rest under the shade of date palm trees, Rasool entered in the bushes nearby which belonged to a man from Ansaar. Suddenly a camel came towards him weeping tenderly with its eyes welling with tears. When the camel reached Rasool it began to groan and its eyes flowed with tears. Holy Rasool patted on its hump and the base of its head until the camel quieted down. Then, He asked \"who is the owner of this camel?\" a young man came forward and said \"it is mine, O Messenger of Allah.\" Rasool said \"Do you not fear Allah with regard to this creature which He has placed in your possession? It has complained to me that you starve it and put it to extreme work.\" (Abu Dawood-2549) The young man understood the words of Rasool and then the Holy Rasool and his companions continued their journey.",
            "definitions": {
                "Ansaar": "The helpers; people of Medina who supported the Holy Rasool",
                "weeping tenderly": "Crying softly or gently",
                "welling with tears": "Filling with tears",
                "groan": "Make a deep sound because of pain or distress",
                "hump": "The raised part on a camel's back"
            },
            "comprehension_check": {
                "question": "What did the camel complain about to the Holy Rasool?",
                "answer": "That its owner starved it and put it to extreme work"
            }
        }
    ]

    # Display reading content with interactive elements
    for i, section in enumerate(processed_content):
        with st.container():
            st.write(section["paragraph"])

            # Create columns for the interactive elements
            col1, col2 = st.columns(2)

            # Show definitions in the first column
            with col1:
                with st.expander("Definitions"):
                    for term, definition in section["definitions"].items():
                        st.markdown(f"**{term}**: {definition}")

            # Show comprehension check in the second column
            with col2:
                with st.expander("Comprehension Check"):
                    st.write(section["comprehension_check"]["question"])
                    user_answer = st.text_input(f"Your answer for section {i+1}:", key=f"comp_check_{i}")
                    if user_answer:
                        # In a real implementation, this would evaluate the answer against the correct one
                        correct_answer = section["comprehension_check"]["answer"]
                        if user_answer.lower() in correct_answer.lower():
                            st.success("Correct! " + correct_answer)
                        else:
                            st.error(f"Try again. Hint: {correct_answer[0:3]}...")

            st.divider()

    # Button to proceed to post-reading
    if st.button("I've Finished Reading"):
        st.session_state.selected_phase = "post_reading"
        st.rerun()


def show_post_reading_view(book_tutor, chapter_id):
    """
    Show post-reading phase view.

    Args:
        book_tutor: BookTutor instance
        chapter_id: ID of the current chapter
    """
    st.header("Post-Reading Activities")

    # This would normally call book_tutor.generate_post_reading_content(chapter_id)
    # For demonstration, we'll use placeholder data
    post_reading_content = {
        "summary_prompts": [
            "In your own words, summarize the key teachings about kindness from this chapter.",
            "Explain how the Holy Rasool demonstrated kindness to animals in the examples from the chapter."
        ],
        "discussion_questions": [
            "Why do you think kindness to animals is emphasized in the teachings of the Holy Rasool?",
            "How can we apply these teachings about kindness in our daily lives?"
        ],
        "concept_mapping": {
            "central_concept": "Kindness of the Holy Rasool",
            "related_concepts": [
                "Kindness to humans",
                "Kindness to animals",
                "Emotional wellbeing of creatures",
                "Role model for humanity"
            ]
        }
    }

    # Summary section
    st.subheader("Summary")
    for i, prompt in enumerate(post_reading_content["summary_prompts"]):
        st.write(prompt)
        user_summary = st.text_area(f"Your summary for prompt {i+1}:", key=f"summary_{i}")
        if user_summary:
            # In a real implementation, this would send the summary to the AI for feedback
            st.success("✓ Summary saved")
        st.divider()

    # Discussion questions
    st.subheader("Discussion Questions")
    for i, question in enumerate(post_reading_content["discussion_questions"]):
        st.write(question)
        user_response = st.text_area(f"Your thoughts on question {i+1}:", key=f"disc_{i}")
        if user_response:
            # In a real implementation, this would send the response to the AI for feedback
            st.success("✓ Response saved")
        st.divider()

    # Concept mapping
    st.subheader("Concept Map")
    st.write("Connect the following concepts to the central concept of 'Kindness of the Holy Rasool':")
    for concept in post_reading_content["concept_mapping"]["related_concepts"]:
        st.write(f"- {concept}")

    # Button to proceed to assessment
    if st.button("Continue to Assessment"):
        st.session_state.selected_phase = "assessment"
        st.rerun()


def show_assessment_view(book_tutor, chapter_id):
    """
    Show assessment phase view.

    Args:
        book_tutor: BookTutor instance
        chapter_id: ID of the current chapter
    """
    st.header("Assessment")

    # Get difficulty and question types from session state
    difficulty = st.session_state.get("difficulty", "medium")
    question_types = st.session_state.get("question_types", ["multiple_choice", "short_answer", "true_false"])

    # This would normally call book_tutor.generate_assessment(chapter_id, difficulty, question_types)
    # For demonstration, we'll use placeholder data
    assessment_content = {
        "multiple_choice": [
            {
                "question": "Who did the Holy Rasool advise his companions to be kind to?",
                "options": [
                    "Only Muslims",
                    "Only humans",
                    "All lives around them, without discrimination",
                    "Only the elderly"
                ],
                "correct_answer": "All lives around them, without discrimination",
                "explanation": "The Holy Rasool repeatedly advised his companions to be kind to all lives around them, without any discrimination."
            }
        ],
        "short_answer": [
            {
                "question": "What title did Allah Almighty bestow upon the Holy Rasool?",
                "correct_answer": "Benefactor of all the worlds",
                "keywords": ["benefactor", "worlds"]
            }
        ],
        "true_false": [
            {
                "question": "The Holy Rasool was only concerned about the physical health of animals.",
                "correct_answer": False,
                "explanation": "The Holy Rasool was concerned about both the physical health and emotional conditions of animals."
            }
        ]
    }

    # Display the assessment questions based on the selected question types
    st.subheader(f"Chapter {chapter_id} Assessment ({difficulty.capitalize()} Difficulty)")

    # Multiple choice questions
    if "multiple_choice" in question_types and assessment_content["multiple_choice"]:
        st.subheader("Multiple Choice Questions")
        for i, question in enumerate(assessment_content["multiple_choice"]):
            st.write(f"**{i+1}. {question['question']}**")
            options = question["options"]
            selected_option = st.radio("Select one:", options, key=f"mc_{i}")

            # Check button for each question
            check_key = f"check_mc_{i}"
            if st.button("Check Answer", key=check_key):
                if selected_option == question["correct_answer"]:
                    st.success("Correct! " + question["explanation"])
                else:
                    st.error("Incorrect. " + question["explanation"])
            st.divider()

    # Short answer questions
    if "short_answer" in question_types and assessment_content["short_answer"]:
        st.subheader("Short Answer Questions")
        for i, question in enumerate(assessment_content["short_answer"]):
            st.write(f"**{i+1}. {question['question']}**")
            user_answer = st.text_input("Your answer:", key=f"sa_{i}")

            # Check button for each question
            check_key = f"check_sa_{i}"
            if st.button("Check Answer", key=check_key):
                correct = any(keyword.lower() in user_answer.lower() for keyword in question["keywords"])
                if correct:
                    st.success(f"Correct! The answer is '{question['correct_answer']}'.")
                else:
                    st.error(f"Incorrect. The answer is '{question['correct_answer']}'.")
            st.divider()

    # True/False questions
    if "true_false" in question_types and assessment_content["true_false"]:
        st.subheader("True/False Questions")
        for i, question in enumerate(assessment_content["true_false"]):
            st.write(f"**{i+1}. {question['question']}**")
            options = ["True", "False"]
            selected_option = st.radio("Select one:", options, key=f"tf_{i}")

            # Check button for each question
            check_key = f"check_tf_{i}"
            if st.button("Check Answer", key=check_key):
                correct = (selected_option == "True" and question["correct_answer"]) or (selected_option == "False" and not question["correct_answer"])
                if correct:
                    st.success("Correct! " + question["explanation"])
                else:
                    st.error("Incorrect. " + question["explanation"])
            st.divider()

    # Button to proceed to critical thinking
    if st.button("Continue to Critical Thinking"):
        st.session_state.selected_phase = "critical_thinking"
        st.rerun()


def show_critical_thinking_view(book_tutor, chapter_id):
    """
    Show critical thinking phase view.

    Args:
        book_tutor: BookTutor instance
        chapter_id: ID of the current chapter
    """
    st.header("Critical Thinking")

    # This would normally call book_tutor.generate_critical_thinking_prompts(chapter_id)
    # For demonstration, we'll use placeholder data
    critical_thinking_content = {
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

    # Reflection questions
    st.subheader("Reflection Questions")
    for i, question in enumerate(critical_thinking_content["reflection_questions"]):
        st.write(f"**{i+1}. {question}**")
        user_reflection = st.text_area(f"Your reflection on question {i+1}:", key=f"refl_{i}")
        if user_reflection:
            # In a real implementation, this would send the reflection to the AI for feedback
            st.success("✓ Reflection saved")
        st.divider()

    # Scenarios
    st.subheader("Scenarios to Consider")
    for i, scenario_data in enumerate(critical_thinking_content["scenarios"]):
        st.write(f"**Scenario {i+1}:**")
        st.write(scenario_data["scenario"])

        for j, question in enumerate(scenario_data["questions"]):
            st.write(f"- {question}")
            user_response = st.text_area(f"Your response to scenario {i+1}, question {j+1}:", key=f"scen_{i}_{j}")
            if user_response:
                # In a real implementation, this would send the response to the AI for feedback
                st.success("✓ Response saved")
        st.divider()

    # Connections
    st.subheader("Making Connections")
    for i, connection_prompt in enumerate(critical_thinking_content["connections"]):
        st.write(f"**{i+1}. {connection_prompt}**")
        user_connection = st.text_area(f"Your thoughts on connection {i+1}:", key=f"conn_{i}")
        if user_connection:
            # In a real implementation, this would send the connection to the AI for feedback
            st.success("✓ Connection saved")
        st.divider()

    # Button to complete the chapter
    if st.button("Complete Chapter"):
        st.success("Congratulations! You've completed Chapter 1.")
        # In a real implementation, this would update the student's progress
        st.balloons()
