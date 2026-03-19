# Flash Denken 🧠🇳🇱

**Flash Denken** is an advanced Dutch language learning application designed to bridge the gap between passive vocabulary recognition and active, intuitive usage. Built with Python and Streamlit, it leverages Generative AI (Google Gemini) to create deep, context-rich learning materials and employs the Ebisu algorithm for optimized spaced repetition.

## 🚀 Key Features

*   **AI-Powered Word Analysis**: Generates comprehensive linguistic profiles for words, including nuance, formality, collocations, and etymology.
*   **The "Thought Scenario" Method**: Teaches words by simulating the internal monologue and situation that precedes speech, helping learners internalize *why* a word is chosen.
*   **Active Recall Testing**: Generates dynamic, context-based prompts (not just definitions) to test memory retention.
*   **Spaced Repetition (SRS)**: Uses the Ebisu algorithm to schedule reviews based on memory half-life probabilities.
*   **Multimedia Support**: Allows users to attach personal images and videos to words to strengthen memory anchors.

---

## 🔬 System Philosophy & Design

### Scientific Philosophy

1.  **Beyond Translation**: The core pedagogical belief is that translation is insufficient for fluency. Flash Denken uses **"Thought Scenarios"** (Situation → Internal Monologue → Expression) to map the pre-linguistic thought directly to the target Dutch word, bypassing English translation where possible.
2.  **Contextual Anchoring**: Words are never learned in isolation. They are presented within a **Relational Web** (synonyms, antonyms) and **Contextual Info** (formality, common mistakes) to build a semantic network in the learner's mind.
3.  **Active Recall**: The system rejects simple multiple-choice questions. Users must generate the word from memory based on specific creative prompts (e.g., "Slice of Life", "Problem Solution", "Sensory Emotional").
4.  **Probabilistic Scheduling**: We use **Ebisu**, a Bayesian model for spaced repetition, to handle the uncertainty of memory and predict the optimal time to review a word.

### Programmatic Philosophy

1.  **Structured Generation**: We do not rely on unstructured free-text LLM outputs. We use **Pydantic models** (`output_models.py`) to enforce strict JSON schemas for all AI generation, ensuring data integrity, type safety, and parseability across the application.
2.  **Stateless UI with State Management**: Built on **Streamlit**, the app handles complex user flows (learning sessions, exams) by carefully managing `st.session_state`.
3.  **Separation of Concerns**: Business logic (DB operations, API calls) is strictly separated from UI rendering components (`tabs/` directory), making the code modular and testable.
4.  **Data Persistence**: A robust **SQLite** schema (`create_db.py`) stores not just words, but the relationships, user-generated media, and detailed history of practice sessions to track progress over time.

---

## 📂 Codebase Hierarchy & Guide

The project follows a modern `src` layout for clean separation between source code and project root files.

### 1. Application Root
- **`app.py`**: The main entry point for the Streamlit application.
- **`create_db.py`**: A one-time script to initialize the SQLite database and its schema.
- **`requirements.txt`**: Lists all project dependencies.
- **`README.md`**: You are here!

### 2. Main Source (`src/flash_denken/`)
This directory contains the core logic of the application.

#### 2.1. Configuration & State Management
- **`parameters.py`**: A dataclass that holds all application-wide parameters, from API keys and model names to file paths and algorithm settings. It's the central configuration hub.
- **`state_manager.py`**: Manages the Streamlit session state (`st.session_state`), ensuring all required variables are initialized correctly when the app starts.

#### 2.2. Core Data Models & AI Instructions
- **`output_models.py`**: Defines the "nervous system" of the app. Contains all Pydantic models (`WordAnalysis`, `HerinneringsTest`, etc.) that enforce strict, predictable data structures for all data flowing through the application, especially from the AI.
- **`instructions.py`**: Stores the large, detailed system prompts (`WORD_ANALYSIS`, `RECALL_GENERATION`) that instruct the Gemini LLM on its pedagogical goals and required output format.

#### 2.3. AI, Spaced Repetition, and Persistence
- **`gemini.py`**: The dedicated interface for the Google Gemini API. It handles making requests, managing API configurations, and parsing the JSON responses back into Pydantic objects.
- **`db_operations.py`**: The persistence layer. A comprehensive library of CRUD (Create, Read, Update, Delete) functions for interacting with the SQLite database. It encapsulates all SQL logic.
- **`ebisu_tools.py`**: Contains all logic related to the Ebisu spaced repetition algorithm. It includes functions to calculate recall probabilities and update the Ebisu parameters for each word after a practice session.

#### 2.4. User Interface (UI)
- **`html_generation.py`**: The presentation engine. This module is responsible for generating the rich, styled HTML and CSS used to display the word analysis cards and recall prompts, making the learning experience visually engaging.
- **`tabs/`**: This sub-package contains the Python modules that build the different tabs in the Streamlit UI.
    - `learning/learning_tab_widgets.py`: Contains all the widgets and logic for the "Learning" tab, where users study new words and add personal media.
    - `recall/recall_tab_widgets.py`: Contains all widgets and logic for the "Recall" tab, which implements the spaced repetition testing loop.

#### 2.5. Utilities
- **`utils.py`**: A collection of essential helper functions used across the application, such as string parsers, URL validators, and list chunking tools.

---

## 🛠️ Installation & Usage

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd flash_denken
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit google-genai pydantic pandas pillow ebisu
    ```

3.  **Initialize Database**
    Creates the local SQLite database file.
    ```bash
    python create_db.py
    ```

4.  **Run the Application**
    Launch the Streamlit interface.
    ```bash
    streamlit run app.py
    ```
    *(Note: Ensure your Google Gemini API key is configured within the application settings or environment variables).*

(This README is co-written by me and Gemini)
