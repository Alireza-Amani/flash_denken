'''This script creates the SQLite database schema for the vocabulary application.'''

import sqlite3

SQL_STATEMENT = """
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
CREATE TABLE IF NOT EXISTS practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

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
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- New field added here
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recall_prompts_word_id ON recall_prompts(word_id);
CREATE INDEX IF NOT EXISTS idx_recall_prompts_category ON recall_prompts(category);
-- Add an index for the new column if you plan to query by it often
CREATE INDEX IF NOT EXISTS idx_recall_prompts_last_used_at ON recall_prompts(last_used_at);

"""


def create_database(db_path: str) -> None:
    """Creates the SQLite database schema for the vocabulary application."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript(SQL_STATEMENT)
            conn.commit()
        print(f"Database created successfully at {db_path}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    create_database("./data/my_vocabulary.db")
