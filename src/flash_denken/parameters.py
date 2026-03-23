from pathlib import Path
from dataclasses import dataclass
import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
from .utils import assert_model_presence
from .instructions import WORD_ANALYSIS, RECALL_GENERATION


@dataclass
class Parameters:
    """
    Parameters for the app.
    """

    # Path to the database file
    db_path: Path = Path("data/my_vocabulary.db")

    # path to the image directory
    image_dir: Path = Path("static/images")

    # Google Gemini API key
    gemini_api_key: str = None

    # model name for Gemini API
    gemini_model_name: str = "gemini-2.5-flash"

    # instruction prompt for generating word analyses
    word_analysis_instruction: str = WORD_ANALYSIS

    # instruction prompt for generating recall questions
    recall_generation_instruction: str = RECALL_GENERATION

    # chunk size for processing words
    chunk_size: int = 7

    # chunk size for processing recall questions
    recall_chunk_size: int = 7

    # image resize coefficient
    image_resize_coefficient: float = 0.8

    # datetime format for storing in the database
    datetime_format: str = "%Y-%m-%d %H:%M:%S"

    # ebisu parameters
    ebisu_alpha: float = 4.0
    ebisu_beta: float = 4.0
    ebisu_half_life: int = 24  # hours

    def __post_init__(self):
        # Ensure the file exists
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        if not self.gemini_api_key:
            try:
                load_dotenv(override=True)
                self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            except Exception as e:
                raise Exception("No Gemini API key found") from e

        # ensure the API key is valid
        try:
            client = genai.Client(api_key=self.gemini_api_key)

            # check if the model is available
            assert_model_presence(client, self.gemini_model_name)

        except Exception as e:
            raise ValueError(
                f"Invalid Gemini API key: {self.gemini_api_key}") from e
