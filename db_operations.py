'''
Database operations for the app.

Reminder:

SQL_STATEMENT = """
"""
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    part_of_speech TEXT NOT NULL,
    definition TEXT NOT NULL,
    article TEXT,
    simple_past TEXT,
    past_participle TEXT,
    pronunciation_ipa TEXT NOT NULL,
    nuance TEXT NOT NULL,
    formality TEXT NOT NULL,
    typical_usage TEXT NOT NULL,
    common_mistake TEXT NOT NULL,

    translations_json TEXT NOT NULL,
    comparisons_json TEXT NOT NULL,
    synonyms_json TEXT NOT NULL,
    antonyms_json TEXT NOT NULL,
    collocations_json TEXT NOT NULL,

    learned_at TEXT DEFAULT NULL, -- Date when the word was learned

    -- Ebisu-specific fields
    ebisu_alpha REAL NOT NULL DEFAULT 4.0,       -- Alpha parameter for Ebisu model
    ebisu_beta REAL NOT NULL DEFAULT 4.0,        -- Beta parameter for Ebisu model
    ebisu_halflife REAL NOT NULL DEFAULT 24.0,   -- Half-life in hours for Ebisu model
    ebisu_last_tested_at TEXT DEFAULT NULL,      -- Timestamp of the last quiz for this word

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for 'words' table:
-- The 'word' column is already indexed due to the UNIQUE constraint.
-- Add indexes for Ebisu fields if you plan to query based on them
CREATE INDEX IF NOT EXISTS idx_words_ebisu_last_tested_at ON words(ebisu_last_tested_at);
CREATE INDEX IF NOT EXISTS idx_words_ebisu_halflife ON words(ebisu_halflife);


-- Indexes for 'words' table:
-- The 'word' column is already indexed due to the UNIQUE constraint.
-- If you frequently query by part_of_speech or formality, consider indexing them.
-- For example: CREATE INDEX idx_words_part_of_speech ON words(part_of_speech);
--               CREATE INDEX idx_words_formality ON words(formality);


-- Table for ThoughtScenarios (consolidated system and user-created scenarios)
CREATE TABLE IF NOT EXISTS thought_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    situation TEXT NOT NULL,
    internal_monologue TEXT NOT NULL,
    expression TEXT NOT NULL,
    is_user_created BOOLEAN DEFAULT 0,

    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Indexes for 'thought_scenarios' table:
-- Essential for efficient joining with the 'words' table and looking up scenarios for a specific word.
CREATE INDEX idx_thought_scenarios_word_id ON thought_scenarios(word_id);
-- If you frequently filter by whether a scenario is user-created or not.
CREATE INDEX idx_thought_scenarios_is_user_created ON thought_scenarios(is_user_created);
-- If you search for scenarios by title.
-- CREATE INDEX idx_thought_scenarios_title ON thought_scenarios(title); -- Consider if 'title' is often in WHERE clauses.


-- Table for storing the practice sessions
--- have to add a result column, to store the result of the practice session
CREATE TABLE IF NOT EXISTS practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success INTEGER NOT NULL, -- Indicates if the practice session was successful
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Indexes for 'practice_sessions' table:
-- Essential for efficient joining with the 'words' table and looking up sessions for a specific word.
CREATE INDEX idx_practice_sessions_word_id ON practice_sessions(word_id);
-- Very important if you want to query sessions by date range (e.g., "show me practice sessions from last week").
CREATE INDEX idx_practice_sessions_session_date ON practice_sessions(session_date);


-- Table for storing user created media (images, audio, video)
CREATE TABLE IF NOT EXISTS user_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    content_url TEXT NOT NULL,
    description TEXT,

    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Indexes for 'user_media' table:
-- Essential for efficient joining with the 'words' table and looking up media for a specific word.
CREATE INDEX idx_user_media_word_id ON user_media(word_id);
-- If you frequently filter media by its type (e.g., "show me all images").
CREATE INDEX idx_user_media_content_type ON user_media(content_type);

CREATE TABLE IF NOT EXISTS recall_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    prompt_json TEXT NOT NULL,
    last_used_at TEXT DEFAULT NULL, -- Timestamp of the last time this prompt was used
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recall_prompts_word_id ON recall_prompts(word_id);
CREATE INDEX IF NOT EXISTS idx_recall_prompts_category ON recall_prompts(category);
-- Add an index for the new column if you plan to query by it often
CREATE INDEX IF NOT EXISTS idx_recall_prompts_last_used_at ON recall_prompts(last_used_at);
"""
'''

import sqlite3
import random
import datetime
import json
from typing import List, TYPE_CHECKING, Dict, Optional, Tuple
from collections import defaultdict
import pandas as pd
from pandas import DataFrame
import pydantic
import streamlit as st
from gemini import post_process_analysis
from output_models import TermPrompts, EnkelePrompt

# This is a forward reference to avoid circular imports if AnalysisResult
# if TYPE_CHECKING:
from output_models import (
    AnalysisResult, WordAnalysis, ThoughtScenario,
    CoreMeaning, ContextualInfo, RelationalWeb, Physicality, StringToStringDict,
)


def get_words_already_in_db() -> List[str]:
    """Fetches a list of words already in the database."""

    db_path = st.session_state["parameters"].db_path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT word FROM words")
            words = [row[0] for row in cursor.fetchall()]
        return words
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def save_user_media_to_db(
    word_id: int, content_type: str, content_url: str, description: str
):
    """
    Saves user media (image, audio, video) to the database.

    Parameters
    ----------
    word_id : int
        The ID of the word associated with the media.
    content_type : str
        The type of content (e.g., 'image', 'audio', 'video').
    content_url : str
        The URL or path to the media content.
    description : str
        A description of the media content.
    """
    db_path = st.session_state["parameters"].db_path

    # make sure url is str, if its Path, convert it to str
    if isinstance(content_url, str):
        content_url = content_url.strip()
    else:
        content_url = str(content_url).strip()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_media (word_id, content_type, content_url, description)
                VALUES (?, ?, ?, ?)
                """,
                (word_id, content_type, content_url, description)
            )
            conn.commit()
            print(f"Media saved for word ID {word_id}.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# load user media, givne cursor and type


def load_user_media(word_id: int) -> List[Dict[str, str]]:
    """
    Loads user media for a specific word ID.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The database cursor to execute queries.
    word_id : int
        The ID of the word for which to load media.

    Returns
    -------
    List[Dict]
        A list of dictionaries containing media details.
    """
    db_path = st.session_state["parameters"].db_path
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, content_type, content_url, description
                FROM user_media
                WHERE word_id = ?
                """,
                (word_id,)
            )
            media_records = cursor.fetchall()

            user_media = []  # List[Dict[str, str]]
            for record in media_records:
                media_id, content_type, content_url, description = record
                user_media.append({
                    "id": media_id,
                    "content_type": content_type,
                    "content_url": content_url,
                    "description": description
                })
            return user_media
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def save_analysis_result_to_db(analysis_result: 'AnalysisResult'):
    """
    Saves an AnalysisResult object into the SQLite database, handling word insertion
    or updating, and refreshing associated thought scenarios.

    Parameters
    ----------
    analysis_result : AnalysisResult
        The AnalysisResult object containing word analyses to be saved.

    **kwargs : dict
        Additional parameters to customize the saving process.

    Raises
    ------
    sqlite3.Error
        If there is an error during database operations.
    Exception
        For any other unexpected errors during the process.
    """
    db_path = st.session_state["parameters"].db_path
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        try:
            # Process each word analysis and save it to the database
            _process_word_analyses(cursor, analysis_result.analyses)
            conn.commit()
            print("---")
            print("All word analysis data saved successfully!")
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
            conn.rollback()
        except Exception as e:
            print(
                f"An unexpected error occurred during database operation: {e}")


def _process_word_analyses(cursor: sqlite3.Cursor, word_analyses: list):
    """
    Helper function to process and save individual WordAnalysis objects.
    """
    for i, word_analysis in enumerate(word_analyses):
        print(
            f"\nProcessing word {i+1}/{len(word_analyses)}: '{word_analysis.word}'")
        word_id = _upsert_word(cursor, word_analysis)
        if word_id is not None:
            _save_thought_scenarios(
                cursor, word_id, word_analysis.thought_scenarios)
        else:
            print(
                f"Warning: Could not get ID for word '{word_analysis.word}'. Skipping thought scenarios.")


def _upsert_word(cursor: sqlite3.Cursor, word_analysis) -> int | None:
    """
    Inserts a new word or updates an existing one, returning its ID.
    Uses INSERT OR IGNORE and then UPDATE if the row already exists.
    """

    current_time = datetime.datetime.now().strftime(
        st.session_state["parameters"].datetime_format)
    # Prepare data for the 'words' table, serializing lists/dicts to JSON
    word_data: dict[str, object] = {
        "word": word_analysis.word,
        "part_of_speech": word_analysis.part_of_speech,
        "definition": word_analysis.definition,
        "article": word_analysis.article,
        "simple_past": word_analysis.simple_past,
        "past_participle": word_analysis.past_participle,
        "pronunciation_ipa": word_analysis.physicality.pronunciation_ipa,
        "nuance": word_analysis.meaning.nuance,
        "translations_json": json.dumps(word_analysis.meaning.translation),
        "formality": word_analysis.context.formality,
        "typical_usage": word_analysis.context.typical_usage,
        "common_mistake": word_analysis.context.common_mistake,
        "comparisons_json": json.dumps(word_analysis.context.comparisons),
        "synonyms_json": json.dumps(word_analysis.relations.synonyms),
        "antonyms_json": json.dumps(word_analysis.relations.antonyms),
        "collocations_json": json.dumps(word_analysis.relations.collocations),
        "created_at": current_time,
        "ebisu_alpha": float(st.session_state["ebisu_alpha_input_key"]),
        "ebisu_beta": float(st.session_state["ebisu_beta_input_key"]),
        "ebisu_halflife": float(st.session_state["ebisu_half_life_input_key"]),
    }

    columns = ', '.join(word_data.keys())
    placeholders = ', '.join('?' * len(word_data))
    values = tuple(word_data.values())

    # Attempt to insert the new word
    try:
        cursor.execute(
            f"""
            INSERT OR IGNORE INTO words ({columns})
            VALUES ({placeholders})
            """,
            values,
        )
        word_id = cursor.lastrowid

        if word_id:
            print(
                f"Inserted new word: '{word_analysis.word}' with ID {word_id}.")
            return word_id
        else:
            # Word already exists, retrieve its ID and update its details
            cursor.execute("SELECT id FROM words WHERE word = ?",
                           (word_analysis.word,))
            result = cursor.fetchone()
            if result:
                existing_word_id = result[0]
                print(
                    f"Word '{word_analysis.word}' already exists (ID: {existing_word_id}). Updating details.")

                # Dynamically create the UPDATE statement for better maintainability
                update_set_clauses = ', '.join(
                    f"{col} = ?" for col in word_data.keys() if col != "word")
                update_values = [
                    v for k, v in word_data.items() if k != "word"]
                # Add word for WHERE clause
                update_values.append(word_analysis.word)

                cursor.execute(
                    f"""
                    UPDATE words SET {update_set_clauses}
                    WHERE word = ?
                    """,
                    tuple(update_values)
                )
                return existing_word_id
            else:
                # This case should ideally not happen if UNIQUE constraint is working as expected
                print(
                    f"Error: Could not retrieve ID for existing word '{word_analysis.word}'.")
                return None
    except TypeError as e:
        print("inside _upsert_word")
        print(f"JSON encoding error for word '{word_analysis.word}': {e}")
        return None
    except sqlite3.Error as e:
        print("inside _upsert_word")
        print(
            f"SQLite error during word upsert for '{word_analysis.word}': {e}")
        return None


def _save_thought_scenarios(cursor: sqlite3.Cursor, word_id: int, scenarios: list):
    """
    Saves thought scenarios for a given word ID into the database.
    """
    if not scenarios:
        print(f"No thought scenarios to save for word ID {word_id}.")
        return

    scenario_values = []
    for scenario in scenarios:
        scenario_values.append(
            (word_id, scenario.title, scenario.situation,
             scenario.internal_monologue, scenario.expression, 0)
        )

    # Use executemany for efficiency if there are many scenarios
    cursor.executemany(
        """
        INSERT INTO thought_scenarios (
            word_id, title, situation, internal_monologue, expression, is_user_created
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        scenario_values,
    )
    print(
        f"Inserted {len(scenarios)} new thought scenarios for word ID {word_id}.")


def load_word_analyses_by_ids(word_ids: List[int]) -> List[WordAnalysis]:
    """
    Loads a list of WordAnalysis objects from the SQLite database given their IDs.

    Parameters
    ----------
    word_ids : List[int]
        A list of word IDs to load from the database.

    Returns
    -------
    List[WordAnalysis]
        A list of WordAnalysis objects corresponding to the provided IDs.
        If no IDs are provided, returns an empty list.

    Raises
    ------
    sqlite3.Error
        If there is an error during database operations.
    Exception
        For any other unexpected errors during the loading process.
    """
    if not word_ids:
        print("No word IDs provided. Returning empty list.")
        return []

    db_path = st.session_state["parameters"].db_path

    loaded_analyses: List[WordAnalysis] = []
    placeholders = ', '.join('?' for _ in word_ids)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Step 1: Fetch words data
            # Use fetchall and map rows to a dictionary for easier access by column name
            # Or define a row_factory if you prefer named access (e.g., conn.row_factory = sqlite3.Row)
            cursor.execute(
                f"""
                SELECT
                    id, word, part_of_speech, definition, article,
                    simple_past, past_participle, pronunciation_ipa, nuance,
                    translations_json, formality, typical_usage,
                    comparisons_json, synonyms_json, antonyms_json, common_mistake, collocations_json
                FROM words
                WHERE id IN ({placeholders})
                """,
                word_ids,
            )
            words_data = cursor.fetchall()
            # It's often good practice to store column names if you're fetching all of them
            # For direct indexing like here, it's less critical but useful for debugging.
            col_names = [description[0] for description in cursor.description]

            # Step 2: Fetch all relevant thought scenarios in one go
            all_thought_scenarios = _fetch_thought_scenarios(
                cursor, word_ids, placeholders)

            # Step 3: Reconstruct WordAnalysis objects
            for row in words_data:
                try:
                    # Get ID by name for robustness
                    word_id_from_db = row[col_names.index('id')]
                    # Reconstruct the WordAnalysis object using a helper function
                    word_analysis_obj = _reconstruct_word_analysis(
                        row, col_names, all_thought_scenarios.get(
                            word_id_from_db, [])
                    )
                    if word_analysis_obj:
                        loaded_analyses.append(word_analysis_obj)
                except Exception as e:
                    # Catch errors specific to reconstructing a single word, allowing others to proceed
                    word_name_for_error = row[col_names.index(
                        'word')] if 'word' in col_names else 'UNKNOWN'
                    print(
                        f"Error reconstructing WordAnalysis for ID {word_id_from_db} ('{word_name_for_error}'): {e}")

    except sqlite3.Error as e:
        print(f"Database error during loading: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during loading process: {e}")

    # post process
    loaded_analyses = post_process_analysis(
        AnalysisResult(analyses=loaded_analyses), loader=True).analyses

    return loaded_analyses


def _fetch_thought_scenarios(cursor: sqlite3.Cursor, word_ids: List[int], placeholders: str) -> Dict[int, List[ThoughtScenario]]:
    """
    Helper to fetch and organize thought scenarios by word_id.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        The database cursor to execute queries.
    word_ids : List[int]
        A list of word IDs for which to fetch thought scenarios.
    placeholders : str
        A string of placeholders for the SQL query, e.g., '?, ?, ?'.

    Returns
    -------
    Dict[int, List[ThoughtScenario]]
        A dictionary mapping word IDs to lists of ThoughtScenario objects.
    """
    all_thought_scenarios: Dict[int, List[ThoughtScenario]] = {}
    cursor.execute(
        f"""
        SELECT
            word_id, title, situation, internal_monologue, expression
        FROM thought_scenarios
        WHERE word_id IN ({placeholders})
        """,
        word_ids,
    )
    scenarios_data = cursor.fetchall()

    for scenario_row in scenarios_data:
        word_id = scenario_row[0]
        try:
            scenario_obj = ThoughtScenario(
                title=scenario_row[1],
                situation=scenario_row[2],
                internal_monologue=scenario_row[3],
                expression=scenario_row[4]
            )
            all_thought_scenarios.setdefault(word_id, []).append(scenario_obj)
        except pydantic.ValidationError as e:
            print(
                f"Pydantic validation error for thought scenario (word_id: {word_id}): {e}")
        except Exception as e:
            print(
                f"Error processing thought scenario for word_id: {word_id}: {e}")

    return all_thought_scenarios


def _reconstruct_word_analysis(
    row: tuple, col_names: List[str], thought_scenarios_list: List[ThoughtScenario]
) -> Optional[WordAnalysis]:
    """
    Helper function to reconstruct a single WordAnalysis object from a database row.
    """
    # Create a dictionary from row and column names for easier, more readable access
    row_dict = dict(zip(col_names, row))

    try:
        # Deserialize JSON strings back to Python objects
        translations = json.loads(row_dict['translations_json'])
        comparisons_raw = json.loads(row_dict['comparisons_json'])
        print(f"{type(comparisons_raw)=}: {row_dict['comparisons_json']}")
        print("-" * 80)

        # --- IMPORTANT: Re-evaluating `serialize_comparisons_dict_to_string` ---
        # If `comparisons` in your Pydantic model (ContextualInfo) is expected to be
        # a dictionary, then `comparisons_raw` (which is already a dict from json.loads)
        # should be used directly.
        # If `comparisons` is expected to be a *string* representation of a dictionary,
        # then `str(comparisons_raw)` or `json.dumps(comparisons_raw)` would be correct.
        # The original code's `serialize_comparisons_dict_to_string(json.loads(comparisons_json))`
        # seems redundant unless that function specifically transforms the dictionary
        # into a *different* string format than what json.dumps produces.
        # For typical Pydantic models expecting a dict, just use comparisons_raw.
        # I'm making an assumption here that ContextualInfo.comparisons expects a dict.
        # If it truly expects a special string format, adjust this line:
        # Assuming ContextualInfo.comparisons expects a dict.
        # comparisons = json.dumps(comparisons_raw) if isinstance(
        #     comparisons_raw, dict) else comparisons_raw
        # Assuming it's a dict directly from JSON
        comparisons = str(comparisons_raw) if isinstance(
            comparisons_raw, dict) else comparisons_raw
        print(f"{type(comparisons)=}: {comparisons}")
        print("-" * 80)
        # If it expects a dict, it might be: comparisons = comparisons_raw
        # If it expects a string representation of the dict, it might be:
        # comparisons = serialize_comparisons_dict_to_string(comparisons_raw)
        # If it expects a string, it might be: comparisons = str(comparisons_raw) or json.dumps(comparisons_raw)

        synonyms = json.loads(row_dict['synonyms_json'])
        antonyms = json.loads(row_dict['antonyms_json'])
        collocations = json.loads(row_dict['collocations_json'])

        # Reconstruct nested Pydantic models
        meaning_obj = CoreMeaning(
            translation=translations, nuance=row_dict['nuance']
        )
        context_obj = ContextualInfo(
            formality=row_dict['formality'],
            comparisons=comparisons,
            typical_usage=row_dict['typical_usage'],
            common_mistake=row_dict.get(
                'common_mistake', None)  # Optional field
        )
        relations_obj = RelationalWeb(
            synonyms=synonyms, antonyms=antonyms, collocations=collocations
        )
        physicality_obj = Physicality(
            pronunciation_ipa=row_dict['pronunciation_ipa']
        )

        # Reconstruct the main WordAnalysis object
        word_analysis_obj = WordAnalysis(
            word=row_dict['word'],
            part_of_speech=row_dict['part_of_speech'],
            definition=row_dict['definition'],
            article=row_dict['article'],
            simple_past=row_dict['simple_past'],
            past_participle=row_dict['past_participle'],
            meaning=meaning_obj,
            context=context_obj,
            relations=relations_obj,
            physicality=physicality_obj,
            thought_scenarios=thought_scenarios_list,
        )
        return word_analysis_obj

    except json.JSONDecodeError as e:
        # Include the specific JSON string that failed for better debugging
        failed_jsons = {k: row_dict[k] for k in [
            'translations_json', 'comparisons_json', 'synonyms_json', 'antonyms_json']}
        print(
            f"JSON decode error for word '{row_dict.get('word', 'N/A')}' (ID: {row_dict.get('id', 'N/A')}). Failed data: {failed_jsons}. Error: {e}")
        return None
    except pydantic.ValidationError as e:
        print(
            f"Pydantic validation error for word '{row_dict.get('word', 'N/A')}' (ID: {row_dict.get('id', 'N/A')}): {e}")
        return None
    except KeyError as e:
        print(
            f"Missing expected column '{e}' when reconstructing word analysis for row: {row_dict}. Check DB schema/SELECT query.")
        return None
    except Exception as e:
        print(
            f"An unexpected error occurred during reconstruction of word '{row_dict.get('word', 'N/A')}' (ID: {row_dict.get('id', 'N/A')}): {e}")
        return None

# ------ end of save/load functions --------------------------------------------

# a function to get an id, and ThoughtScenario, and save it to the thought_scenarios table


def save_user_thought_scenario(
    word_id: int, thought_scenario: ThoughtScenario, is_user_created: bool = True
):
    """
    Saves a user-created ThoughtScenario to the database.
    """
    db_path = st.session_state["parameters"].db_path

    # determine if the fields are not empty (less than 4 characters)
    if not all(len(field) >= 4 for field in [
        # thought_scenario.title,
        thought_scenario.situation,
        thought_scenario.internal_monologue,
        thought_scenario.expression
    ]):
        print("Thought scenario fields must be at least 4 characters long.")
        return

    print(
        f"Saving user thought scenario for word ID {word_id}: {thought_scenario}")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO thought_scenarios (word_id, title, situation, internal_monologue, expression, is_user_created)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (word_id, thought_scenario.title, thought_scenario.situation,
                 thought_scenario.internal_monologue, thought_scenario.expression, is_user_created)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def get_words_practice_tables():
    """
    Fetches the 'words', 'practice_sessions', and 'recall_prompts' tables from the SQLite database
    and returns them as pandas DataFrames. It will update the session state with these DataFrames.
    """

    db_path = st.session_state["parameters"].db_path
    statement_1 = """
    SELECT
        w.id, w.word, w.part_of_speech, w.definition,
        w.created_at, w.learned_at, w.ebisu_last_tested_at,
        w.ebisu_alpha, w.ebisu_beta, w.ebisu_halflife
    FROM words w
    ORDER BY w.created_at DESC;
    """

    statement_2 = """
    SELECT
        ps.id, w.word, ps.session_date, ps.success
    FROM practice_sessions ps
    JOIN words w ON ps.word_id = w.id
    ORDER BY ps.session_date DESC;
    """

    statement_3 = """
    SELECT
        rp.id, w.word, rp.prompt_json, rp.category, rp.last_used_at
    FROM recall_prompts rp
    JOIN words w ON rp.word_id = w.id
    """

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Fetch words table
            words_df = pd.read_sql_query(statement_1, conn)
            # Fetch practice sessions table
            practice_df = pd.read_sql_query(statement_2, conn)

            # Fetch recall prompts table
            recall_prompts_df = pd.read_sql_query(statement_3, conn)

        # Convert to datetime
        dt_format = st.session_state["parameters"].datetime_format
        words_df['created_at'] = pd.to_datetime(
            words_df['created_at'], format=dt_format)

        words_df['learned_at'] = pd.to_datetime(
            words_df['learned_at'], format=dt_format)

        words_df['ebisu_last_tested_at'] = pd.to_datetime(
            words_df['ebisu_last_tested_at'], format=dt_format)

        practice_df['session_date'] = pd.to_datetime(
            practice_df['session_date'], format=dt_format)

        recall_prompts_df['last_used_at'] = pd.to_datetime(
            recall_prompts_df['last_used_at'], format=dt_format)

        st.session_state["words_table_df"] = words_df
        st.session_state["practice_table_df"] = practice_df
        st.session_state["recall_prompts_table_df"] = recall_prompts_df

    except sqlite3.Error as e:
        print("inside get_words_practice_tables 1")
        print(f"Database error: {e}")
    except Exception as e:
        print("inside get_words_practice_tables 2")
        print(f"Unexpected error: {e}")

# find ids, given words


def get_ids_given_words(words: List[str]) -> Dict[int, Dict[str, object]]:
    """
    Fetches the IDs of the given words from the 'words' table in the SQLite database.

    Parameters
    ----------
    words : List[str]
        A list of words for which to fetch IDs.

    Returns
    -------
    Dict[int, Dict[str, object]]
        A dictionary mapping word IDs to their corresponding word information.
    """
    db_path = st.session_state["parameters"].db_path

    if not words:
        return {}
    else:
        words = [word.strip().lower() for word in words if word.strip()]

    placeholders = ', '.join('?' for _ in words)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, word FROM words WHERE word IN ({placeholders})", words)
            rows = cursor.fetchall()
            ids_words_dict: Dict[int, Dict[str, object]] = {row[0]: {"word": row[1],
                                                                     "learned": False} for row in rows}

        return ids_words_dict
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}


def sample_words_to_learn(number_of_words: int) -> List[WordAnalysis]:
    """
    Samples a specified number of words that have not been learned yet from the database.

    Parameters
    ----------
    number_of_words : int
        The number of words to sample.

    Returns
    -------
    List[WordAnalysis]
        A list of WordAnalysis objects representing the sampled words.
    """
    db_path = st.session_state["parameters"].db_path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id FROM words WHERE learned_at IS NULL
                ORDER BY RANDOM() LIMIT ?
                """,
                (number_of_words,)
            )
            word_ids = [row[0] for row in cursor.fetchall()]

        if not word_ids:
            print("No words available to learn.")
            return []

        return load_word_analyses_by_ids(word_ids)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def mark_word_as_learned(word_id: int):
    """
    Marks a word as learned by updating its 'learned_at' timestamp in the database.

    Parameters
    ----------
    word_id : int
        The ID of the word to mark as learned.
    """
    db_path = st.session_state["parameters"].db_path
    current_time = datetime.datetime.now().strftime(
        st.session_state["parameters"].datetime_format)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE words
                SET learned_at = ?
                WHERE id = ?
                """,
                (current_time, word_id)
            )
            conn.commit()
            print(f"Word ID {word_id} marked as learned.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def save_term_prompts_to_db(term_prompts_list: List[TermPrompts]) -> None:
    """
    Saves a list of TermPrompts objects into the recall_prompts table.
    Each individual prompt (EnkelePrompt) from the TermPrompts list is stored
    as a separate row, linked to its corresponding word_id.
    """
    db_path = st.session_state["parameters"].db_path
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Iterate through each TermPrompts object
        for term_prompts_obj in term_prompts_list:
            term = term_prompts_obj.term

            # Get the word_id for the current term
            cursor.execute("SELECT id FROM words WHERE word = ?", (term,))
            result = cursor.fetchone()

            if result:
                word_id = result[0]

                # Insert each individual prompt
                for prompt in term_prompts_obj.prompts:
                    # Use .model_dump_json() for Pydantic v2+
                    prompt_json = prompt.model_dump_json()
                    cursor.execute(
                        "INSERT INTO recall_prompts (word_id, category, prompt_json, last_used_at) VALUES (?, ?, ?, ?)",
                        (word_id, prompt.categorie, prompt_json, None)
                    )
            else:
                print(
                    f"Warning: Word '{term}' not found in 'words' table. Prompts not saved for this term.")

        conn.commit()
        print(
            f"Successfully saved prompts for {len(term_prompts_list)} terms.")

    except sqlite3.Error as e:
        print(f"Database error during save: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred during save: {e}")
    finally:
        if conn:
            conn.close()


def load_term_prompts_from_db(terms: Optional[List[str]] = None) -> List[TermPrompts]:
    """
    Loads TermPrompts objects from the recall_prompts table.
    If 'terms' is provided, only loads prompts for those specific terms.
    Otherwise, loads all available prompts.
    """
    db_path = st.session_state["parameters"].db_path
    conn = None
    loaded_prompts: List[TermPrompts] = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
            SELECT
                w.word,
                rp.category,
                rp.prompt_json,
                rp.last_used_at
            FROM
                recall_prompts rp
            JOIN
                words w ON rp.word_id = w.id
        """
        params = ()

        if terms:
            placeholders = ','.join('?' for _ in terms)
            query += f" WHERE w.word IN ({placeholders})"
            params = tuple(terms)

        query += " ORDER BY w.word"  # Order to help with grouping

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Group prompts by term
        prompts_by_term: Dict[str, List[EnkelePrompt]] = {}
        for word, category, prompt_json_str, last_used_at_str in rows:
            if word not in prompts_by_term:
                prompts_by_term[word] = []

            try:
                # Note: 'last_used_at' isn't part of EnkelePrompt model,
                # so we don't need to pass it to the prompt. It's metadata for the DB record.
                prompt = EnkelePrompt.model_validate_json(prompt_json_str)
                prompts_by_term[word].append(prompt)
            except Exception as e:
                print(
                    f"Error parsing prompt JSON for word '{word}': {e}. JSON: {prompt_json_str[:100]}...")
                continue

        for term, prompts_list in prompts_by_term.items():
            loaded_prompts.append(TermPrompts(term=term, prompts=prompts_list))

        print(f"Successfully loaded prompts for {len(loaded_prompts)} terms.")
        return loaded_prompts

    except sqlite3.Error as e:
        print(f"Database error during load: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during load: {e}")
    finally:
        if conn:
            conn.close()

    return []

# load N prompts for each word id -> Dict[int, List[EnkelePrompt]]:


def load_n_prompts_for_words(word_ids: List[int], n: int = 3) -> Dict[int, List[EnkelePrompt]]:
    """Loads a specified number of prompts for each word ID from the recall_prompts table.

    Parameters
    ----------
    word_ids : List[int]
        A list of word IDs to load prompts for.
    n : int
        The number of prompts to load for each word ID.

    Returns
    -------
    Dict[int, List[EnkelePrompt]]
        A dictionary mapping word IDs to their corresponding prompts.
    """
    db_path = st.session_state["parameters"].db_path
    prompts_by_word: Dict[int, List[EnkelePrompt]] = defaultdict(list)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for word_id in word_ids:
                # random n prompts for each word_id
                cursor.execute(
                    """
                    SELECT prompt_json, word_id
                    FROM recall_prompts
                    WHERE word_id = ?
                    """,
                    (word_id,)
                )
                rows = cursor.fetchall()
                prompt_list = []
                for row in rows:
                    prompt = EnkelePrompt.model_validate_json(row[0])
                    prompt_list.append(prompt)

                # pick `n` unique random prompts
                # shuffle the list and take the first `n` elements
                if len(prompt_list) > n:
                    random.shuffle(prompt_list)

                prompt_list = prompt_list[:n]

                prompts_by_word[word_id] = prompt_list

            print(f"Loaded prompts for {len(prompts_by_word)} words.")

    except sqlite3.Error as e:
        print("inside load_n_prompts_for_words")
        print(f"Database error during load: {e}")
    except Exception as e:
        print("inside load_n_prompts_for_words 2")
        print(f"An unexpected error occurred during load: {e}")

    return prompts_by_word


def find_word_without_prompts() -> List[str]:
    """
    Finds words in the 'words' table that do not have any associated prompts in the 'recall_prompts' table.

    Returns
    -------
    List[str]
        A list of word IDs that do not have any prompts.
    """
    db_path = st.session_state["parameters"].db_path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

           # here we want to have set(ids in word table) - set(ids in recall_prompts table)
            cursor.execute(
                """
                SELECT w.word
                FROM words w
                LEFT JOIN recall_prompts rp ON w.id = rp.word_id
                WHERE rp.word_id IS NULL
                """
            )
            word_ids_without_prompts = [row[0] for row in cursor.fetchall()]

            return word_ids_without_prompts

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def get_word_ids_and_ebisu_params() -> List[Tuple[int, float, float, float, str, str]]:
    """
    Retrieves all word IDs along with their Ebisu parameters and two timestamps.

    Returns
    -------
    List[Tuple[int, float, float, float, str, str]]
        A list of tuples containing word ID, Ebisu parameters (alpha, beta, halflife),
        and two timestamps (last tested at, learned at).
    """

    db_path = st.session_state["parameters"].db_path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            SELECT w.id, w.ebisu_alpha, w.ebisu_beta, w.ebisu_halflife,
            w.ebisu_last_tested_at, w.learned_at
            FROM words w
            """
            )
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

# lets have two functions
# first: give me a list of IDs, and I remove those words and their corresponding
# material from the database

# second, give me list of words, and I remove those words and their corresponding


def remove_words_by_ids(word_ids: List[int]) -> None:
    """
    Removes words and their associated data from the database based on a list of word IDs.

    Parameters
    ----------
    word_ids : List[int]
        A list of word IDs to remove from the database.
    """
    if not word_ids:
        print("No word IDs provided for removal.")
        return

    db_path = st.session_state["parameters"].db_path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Delete thought scenarios first to maintain referential integrity
            cursor.execute(
                "DELETE FROM thought_scenarios WHERE word_id IN ({})".format(
                    ','.join('?' * len(word_ids))),
                word_ids
            )

            # Delete from recall_prompts table
            cursor.execute(
                "DELETE FROM recall_prompts WHERE word_id IN ({})".format(
                    ','.join('?' * len(word_ids))),
                word_ids
            )

            # Delete from practice_sessions table
            cursor.execute(
                "DELETE FROM practice_sessions WHERE word_id IN ({})".format(
                    ','.join('?' * len(word_ids))),
                word_ids
            )

            # Delete from user_media table
            cursor.execute(
                "DELETE FROM user_media WHERE word_id IN ({})".format(
                    ','.join('?' * len(word_ids))),
                word_ids
            )

            # Finally, delete from words table
            cursor.execute(
                "DELETE FROM words WHERE id IN ({})".format(
                    ','.join('?' * len(word_ids))),
                word_ids
            )

            conn.commit()
            print(f"Removed {len(word_ids)} words and their associated data.")

    except sqlite3.Error as e:
        print("inside remove_words_by_ids")
        print(f"Database error during removal: {e}")
    except Exception as e:
        print("inside remove_words_by_ids 2")
        print(f"Unexpected error during removal: {e}")


def remove_words_by_terms(terms: List[str]) -> None:
    """
    Removes words and their associated data from the database based on a list of terms.

    Parameters
    ----------
    terms : List[str]
        A list of terms (words) to remove from the database.
    """
    if not terms:
        print("No terms provided for removal.")
        return

    # Get IDs for the provided terms
    word_ids = list(get_ids_given_words(terms).keys())
    if not word_ids:
        print("No matching words found for the provided terms.")
        return

    # Call the function to remove by IDs
    remove_words_by_ids(word_ids)

# load thought scenarios by word ID


def load_thought_scenarios_by_word_id(word_id: int) -> Dict[int, ThoughtScenario]:
    """
    Loads thought scenarios for a specific word ID from the database.

    Parameters
    ----------
    word_id : int
        The ID of the word for which to load thought scenarios.

    Returns
    -------
    Dict[int, ThoughtScenario]
        A dictionary mapping ID to a ThoughtScenario object.
        If no scenarios are found, returns an empty dictionary.
    """
    db_path = st.session_state["parameters"].db_path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, situation, internal_monologue, expression
                FROM thought_scenarios
                WHERE word_id = ?
                """,
                (word_id,)
            )
            rows = cursor.fetchall()

        thought_scenarios: Dict[int, ThoughtScenario] = {}
        for row in rows:
            try:
                thought_scenario = ThoughtScenario(
                    title=row[1],
                    situation=row[2],
                    internal_monologue=row[3],
                    expression=row[4]
                )
                thought_scenarios[row[0]] = thought_scenario
            except pydantic.ValidationError as e:
                print(
                    f"Pydantic validation error for thought scenario (ID: {row[0]}): {e}")
            except Exception as e:
                print(
                    f"Error processing thought scenario (ID: {row[0]}): {e}")

        return thought_scenarios

    except sqlite3.Error as e:
        print(f"Database error during loading thought scenarios: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error during loading thought scenarios: {e}")
        return {}


# basically update the records
# if corresponding value's title is "DELETE",
# we will delete the record from the table
# get the dict from the previous function, which has the id for the record in the talbe
def save_thought_scenarios_by_word_id(
    word_id: int, thought_scenarios: Dict[int, ThoughtScenario]
) -> None:
    """Updates thought scenarios for a specific word ID in the database.

    Parameters
    ----------
    word_id : int
        The ID of the word for which to update thought scenarios.
    thought_scenarios : Dict[int, ThoughtScenario]
        A dictionary mapping scenario IDs to ThoughtScenario objects.
        If a scenario's title is "DELETE", it will be removed from the database.
    """
    db_path = st.session_state["parameters"].db_path

    if not thought_scenarios:
        print("No thought scenarios provided for update.")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # First, delete scenarios that are marked for deletion
            to_delete_ids = [
                scenario_id for scenario_id, scenario in thought_scenarios.items()
                if scenario.title == "DELETE"
            ]
            if to_delete_ids:
                cursor.execute(
                    "DELETE FROM thought_scenarios WHERE id IN ({})".format(
                        ','.join('?' * len(to_delete_ids))),
                    to_delete_ids
                )
                print(f"Deleted {len(to_delete_ids)} thought scenarios.")

            # Now, insert or update the remaining scenarios
            for scenario_id, scenario in thought_scenarios.items():
                if scenario.title != "DELETE":
                    cursor.execute(
                        """
                        INSERT INTO thought_scenarios (id, word_id, title, situation, internal_monologue, expression)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            title = excluded.title,
                            situation = excluded.situation,
                            internal_monologue = excluded.internal_monologue,
                            expression = excluded.expression
                        """,
                        (scenario_id, word_id, scenario.title,
                         scenario.situation, scenario.internal_monologue, scenario.expression)
                    )

            conn.commit()
            print(f"Updated thought scenarios for word ID {word_id}.")

    except sqlite3.Error as e:
        print(f"Database error during saving thought scenarios: {e}")
    except Exception as e:
        print(f"Unexpected error during saving thought scenarios: {e}")

# same for user image


# id, image_path
def load_user_images_by_word_id(word_id: int) -> Dict[int, str]:
    """Loads user images associated with a specific word ID from the database.

    Parameters
    ----------
    word_id : int
        The ID of the word for which to load user images.

    Returns
    -------
    Dict[int, str]
        A dictionary mapping image IDs to their file paths.
    """
    db_path = st.session_state["parameters"].db_path
    user_images: Dict[int, str] = {}

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content_url FROM user_media WHERE word_id = ? AND content_type = 'image'",
                (word_id,)
            )
            rows = cursor.fetchall()
            for row in rows:
                user_images[row[0]] = row[1]
    except sqlite3.Error as e:
        print(f"Database error during loading user images: {e}")
    except Exception as e:
        print(f"Unexpected error during loading user images: {e}")

    return user_images


def save_user_images_by_word_id(
    word_id: int, user_images: Dict[int, str]
) -> None:
    """Saves or updates user images associated with a specific word ID in the database.

    Parameters
    ----------
    word_id : int
        The ID of the word for which to save user images.
    user_images : Dict[int, str]
        A dictionary mapping image IDs to their file paths.
        If an image's path is "DELETE", it will be removed from the database.
    """
    db_path = st.session_state["parameters"].db_path

    if not user_images:
        print("No user images provided for update.")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # First, delete images that are marked for deletion
            to_delete_ids = [
                image_id for image_id, image_path in user_images.items()
                if image_path == "DELETE"
            ]
            if to_delete_ids:
                cursor.execute(
                    "DELETE FROM user_media WHERE id IN ({})".format(
                        ','.join('?' * len(to_delete_ids))), (to_delete_ids,)
                )
                print(f"Deleted {len(to_delete_ids)} user media.")

            # Now, insert or update the remaining media
            for image_id, image_path in user_images.items():
                if image_path != "DELETE":
                    cursor.execute(
                        """
                        INSERT INTO user_media (id, word_id, content_type, content_url)
                        VALUES (?, ?, 'image', ?)
                        ON CONFLICT(id) DO UPDATE SET
                            content_url = excluded.content_url
                        """,
                        (image_id, word_id, image_path)
                    )

            conn.commit()
            print(f"Updated user images for word ID {word_id}.")

    except sqlite3.Error as e:
        print(f"Database error during saving user images: {e}")
    except Exception as e:
        print(f"Unexpected error during saving user images: {e}")
