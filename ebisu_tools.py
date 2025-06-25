''' XYZ'''
import sqlite3
import math
import pandas as pd
import ebisu
import streamlit as st
#   

SECONDS_IN_HOUR = 3600


def predict_row(row: pd.Series, exact: bool = True) -> float:
    """Calculates the recall probability for a single word using its Ebisu parameters.

    Parameters
    ----------
    row : pd.Series
        A Pandas Series containing the Ebisu parameters and time elapsed for a word.
    exact : bool, optional
        If True, uses the exact prediction method; otherwise, uses the exponential
        of the prediction for a more interpretable probability.
    Returns
    -------
    float
        The recall probability for the word.
    """

    prior = (row['ebisu_alpha'], row['ebisu_beta'], row['ebisu_halflife'])
    if exact:
        probability = ebisu.predictRecall(
            prior, tnow=row['time_elapsed_hours'], exact=exact
        )
    else:
        probability = math.exp(
            ebisu.predictRecall(
                prior, tnow=row['time_elapsed_hours'], exact=exact
            )
        )
    return probability


def calculate_all_recall_probabilities_from_db(exact: bool = True) -> pd.DataFrame:
    """
    Fetches all words from the database, calculates their current recall
    probability using Ebisu, and returns the results in a DataFrame.

    This implementation is optimized for performance using vectorized Pandas operations.

    Parameters
    ----------
    db_path : str
        The file path to the SQLite database.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns for 'word_id' and 'recall_probability',
        sorted by probability in ascending order.
    """
    db_path = st.session_state.parameters.db_path
    try:
        # 1. Fetch data directly into a DataFrame. This is more direct than
        # fetching tuples and then processing them.
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(
                """
                SELECT
                    w.id AS word_id,
                    w.ebisu_alpha,
                    w.ebisu_beta,
                    w.ebisu_halflife,
                    w.ebisu_last_tested_at,
                    w.learned_at
                FROM words w
                """,
                conn
            )
    except (sqlite3.Error, Exception) as e:
        print(f"Database access error: {e}")
        return pd.DataFrame({'word_id': [], 'recall_probability': []})

    if df.empty:
        return pd.DataFrame({'word_id': [], 'recall_probability': []})

    # 2. Vectorized timestamp conversion. Do this once for the entire columns.
    df['ebisu_last_tested_at'] = pd.to_datetime(df['ebisu_last_tested_at'])
    df['learned_at'] = pd.to_datetime(df['learned_at'])

    # 3. Determine the most recent timestamp for each word in a vectorized way.
    df['most_recent_timestamp'] = df[[
        'ebisu_last_tested_at', 'learned_at']].max(axis=1)

    # 4. Get the current time ONCE, outside any loop.
    now = pd.Timestamp.now()

    # 5. Calculate the time difference for all words at once.
    # The .dt accessor provides vectorized datetime properties.
    df['time_elapsed_hours'] = (
        now - df['most_recent_timestamp']).dt.total_seconds() / SECONDS_IN_HOUR

    # 6. Apply the Ebisu function. While `apply` is essentially a loop,
    # all the data preparation leading up to it was vectorized and super fast.
    # This is the step that is hardest to vectorize since `ebisu.predictRecall`
    # expects individual numbers, not arrays.

    df['recall_probability'] = df.apply(
        lambda row: predict_row(row, exact=exact), axis=1
    )

    # 7. Final result: Select and sort the final columns.
    result_df = df[['word_id', 'recall_probability']].sort_values(
        by='recall_probability', ascending=True
    ).reset_index(drop=True)

    return result_df
