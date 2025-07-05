### Enhanced Prompt: Few-Shot + Chain-of-Thought (CrewAI Expert Edition)

**Task**: Update existing CrewAI code to integrate educational content processing (calculus/exercises/reading materials) with Streamlit UI while preserving core functionality. Maintain local LLM integration points.

---

#### **Chain-of-Thought Reasoning**
*(Professional CrewAI/LangChain workflow design)*
1. **Content Processing Pipeline**
   - **Step 1**: Curriculum extraction from files (specify path in code)
   - **Step 2**: Hierarchical content parsing:
     ```mermaid
     graph TD
         A[Chapter File] --> B(Curriculum Metadata)
         A --> C(Pre-reading Questions)
         A --> D(Reading Material)
         A --> E(Post-reading Exercises)
         E --> F[Section A - Basics]
         E --> G[Section B - Applications]
         E --> H[Section C - Challenges]
         E --> I[Section D - Challenges]
     ```

2. **Agent Specialization**
   - **Teaching Agent**: Uses curriculum to sequence learning
   - **Exercise Agent**: Processes sections A/B/C with adaptive difficulty
   - **Monitoring Agent**: Tracks student engagement via Streamlit

3. **Streamlit Integration Strategy**
   - Preserve existing agent backend
   - Build new UI layer with:
     - Chapter selector
     - Exercise progress tracker
     - Real-time engagement dashboard

4. **Critical Preservation Zones**
   - Existing LLM integration points (▼▼▼ marks)
   - CrewAI orchestration logic
   - Local model loading mechanisms

---

#### **Few-Shot Implementation Examples**

**Example 1: Content Loader Tool (Add to Tools)**
```python
# ▼▼▼ SET CONTENT PATH HERE (update with your directory) ▼▼▼
CONTENT_PATH = "/path/to/educational/files"

class ContentLoader:
    def __init__(self):
        self.structure = {
            "chapter": "curriculum_section",
            "pre_reading": "questions",
            "core": "reading_material",
            "exercises": {
                "A": "",
                "B": "",
                "C": ""
                "d": ""
            }
        }

    def load_chapter(self, chapter_id: int):
        """Extract structured content from Markdown/PDF files"""
        chapter_file = f"{CONTENT_PATH}/chapter_{chapter_id}.md"
        # Add your custom parser here (PyPDF2/Unstructured/etc)
        return parsed_content  # Dict matching self.structure

# Add to CrewAI tools
content_tool = Tool(
    name="EducationalContentLoader",
    func=ContentLoader().load_chapter,
    description="Loads curriculum, exercises and reading materials"
)
```

**Example 2: Teaching Agent Update (Preserve LLM Hooks)**
```python
teaching_agent = Agent(
    role="Curriculum Director",
    goal="Sequence learning based on chapter curriculum",
    tools=[content_tool],  # Added content loader
    memory=True,
    rules=[
        "Start with pre-reading questions",
        "Progress through exercises A→B→C",
        "Adjust pace based on student engagement"
    ],
    # ▼▼▼ PRESERVED LLM INTEGRATION POINT ▼▼▼
    llm=local_llms["reasoning_model"],  # Your existing model
    # ▲▲▲
)
```

**Example 3: Streamlit UI Layer (New File: `ui.py`)**
```python
import streamlit as st

# ▼▼▼ CONTENT PATH CONFIGURATION ▼▼▼
st.sidebar.text_input("Content Directory", value="/default/path")

chapter = st.selectbox("Select Chapter", options=[1,2,3,4,5])
if st.button("Load Curriculum"):
    # Uses preserved agent backend
    materials = teaching_agent.run(f"Load chapter {chapter} content")

    st.header(f"Chapter {chapter}: {materials['curriculum']}")
    with st.expander("Pre-reading Questions"):
        st.write(materials["pre_reading"])

    with st.expander("Exercises"):
        tabA, tabB, tabC = st.tabs(["Section A", "Section B", "Section C"])
        tabA.write(materials["exercises"]["A"])
        tabB.write(materials["exercises"]["B"])
        tabC.write(materials["exercises"]["C"])

# Engagement monitoring preserved from existing logic
st.session_state.engagement = monitor_agent.run("Get current engagement")
st.progress(st.session_state.engagement)
```

---

#### **Integration Guide**
1. **File Structure Preservation**
   ```diff
   project/
   ├── main_agent.py   # Original CrewAI code
   ├── tools/          # Existing tools
   + ├── ui.py         # New Streamlit interface
   ├── llm_loader.py   # PRESERVE model loading
   └── crewai_config.yaml
   ```

2. **Targeted Code Changes**
   - Add `ContentLoader` class to tools
   - Insert `CONTENT_PATH` configuration point
   - Create new `ui.py` with streaming components
   - Connect Streamlit to agents via existing `.run()` methods

3. **Critical Preservation Notice**
   > "Existing LLM integration points (marked with ▼▼▼) remain unchanged. Streamlit interacts with agents through preserved public methods. Content loader is isolated new component."

4. **Content Structure Requirements**
   Ensure your educational files contain:
   ```markdown
   ## curriculum_section
   Calculus fundamentals

   ## questions
   - What is derivative?

   ## reading_material
   [Textbook content...]

   ## exercises
   ### Section A
   1.
   ### Section B
   1.
   ### Section C
   1.
   ### Section d
   1.
   ```

**Final Output**: Updated CrewAI system with educational content processing and Streamlit UI while preserving all existing functionality and LLM integration points.