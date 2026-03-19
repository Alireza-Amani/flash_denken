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

This outline explains the role of each file in the system architecture.

### 1. Core Data Structures (`output_models.py`)
Defines the "nervous system" of the app.
*   **`output_models.py`**: Contains Pydantic models (`WordAnalysis`, `ThoughtScenario`, `HerinneringsTest`) that define the data shape. This file ensures that the interface between the Python backend and the Gemini LLM is strictly typed.

### 2. AI & Generation (`gemini.py`, `instructions.py`)
Handles the "brain" of the app.
*   **`gemini.py`**: The interface layer for the Google GenAI SDK. It handles request chunking, API calls, and—crucially—parsing the raw JSON responses into valid Pydantic objects.
*   **`instructions.py`**: Contains the "System Instructions" (`WORD_ANALYSIS`, `RECALL_GENERATION`). These are detailed prompts that instruct the LLM on pedagogical goals (e.g., "Force Active Recall", "Simulate Internal Monologue").

### 3. Persistence Layer (`db_operations.py`, `create_db.py`)
Manages long-term memory.
*   **`create_db.py`**: Initializes the SQLite schema. Creates tables for `words`, `thought_scenarios`, `practice_sessions`, `user_media`, and `recall_prompts`.
*   **`db_operations.py`**: A comprehensive library of CRUD (Create, Read, Update, Delete) operations. It handles complex logic like "upserting" words to prevent duplicates and managing the relationship between words and their generated prompts.

### 4. User Interface (`tabs/`, `html_generation.py`)
The presentation layer.
*   **`tabs/learning/learning_tab_widgets.py`**: Logic for the study interface. Contains widgets for browsing words, adding personal notes, and uploading images/videos.
*   **`tabs/recall/recall_tab_widgets.py`**: Logic for the testing interface. Implements the review loop where users are presented with prompts based on their memory retention.
*   **`html_generation.py`**: A dedicated styling engine that generates HTML/CSS for the word cards. It creates distinct visual themes (e.g., "Scholarly", "Neon Wave") to make learning visually engaging.

### 5. Utilities (`utils.py`)
*   **`utils.py`**: Essential helper functions for string parsing, URL validation, YouTube link embedding, and list chunking.

---

## 🛠️ Installation & Usage

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd flash_denken
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit google-genai pydantic pandas pillow
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
```
