'''Functions for interacting with the Gemini API.'''
import sqlite3
from google import genai
import streamlit as st
from utils import parse_comparisons_string_to_dict, chunk_list, parse_stringified_dict
from output_models import (
    AnalysisResult, StringToStringDict, HerinneringsTest, TermPrompts
)


def post_process_analysis(analysis: AnalysisResult, loader: bool = False) -> AnalysisResult:
    """
    Post-processes the AnalysisResult object to ensure all fields are correctly formatted.

    Parameters
    ----------
    analysis : AnalysisResult
        The AnalysisResult object to post-process.
    loader : bool, optional
        If True, the comparisons are expected to be in a stringified dictionary format.
        If False, they are expected to be in a simple string format. Defaults to False.

    Returns
    -------
    AnalysisResult
        The post-processed AnalysisResult object.
    """

    for idx, _ in enumerate(analysis.analyses):
        word = analysis.analyses[idx]
        if not isinstance(word.context.comparisons, StringToStringDict):
            print(f"Post-processing word: {word.word}")
            print(f"Original comparisons: {word.context.comparisons}")
            print("-" * 80)
            if not loader:
                word.context.comparisons = StringToStringDict(
                    parse_comparisons_string_to_dict(word.context.comparisons)
                )
            else:
                word.context.comparisons = StringToStringDict(
                    parse_stringified_dict(word.context.comparisons)
                )
            print(f"Post-processed comparisons: {word.context.comparisons}")
            print("-" * 80)
    # Ensure the thought scenarios are correctly formatted
    return analysis


def generate_word_analysis(word_list: list[str]) -> AnalysisResult:
    """Generates a structured analysis for a list of Dutch words using the Gemini API.

    Parameters
    ----------
    word_list : list[str]
        A list of Dutch words to analyze.

    Returns
    -------
    AnalysisResult
        An AnalysisResult object containing the analyses for each word.
    """
    if not word_list:
        return AnalysisResult(analyses=[])

    client = genai.Client(
        api_key=st.session_state["parameters"].gemini_api_key)

    chunk_generator = chunk_list(
        word_list, st.session_state["parameters"].chunk_size)

    analyses = []

    for chunk in chunk_generator:
        prompt = ", ".join(chunk)
        try:
            response = client.models.generate_content(
                model=st.session_state["parameters"].gemini_model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AnalysisResult,
                    "system_instruction": st.session_state["parameters"].word_analysis_instruction,
                },
            )
        except Exception as e:
            print(
                f"Er is een fout opgetreden bij het genereren van de analyses: {e}"
            )
            raise e

        try:
            parsed_response = response.parsed
            print("we are inside generate_word_analysis")
            print("-" * 80)
            print(
                f"{type(parsed_response[0].context.comparisons)=}: {parsed_response[0].context.comparisons}"
            )
            print("-" * 80)
            pp_parsed_response = post_process_analysis(parsed_response)
            analyses.extend(
                [word_analysis for word_analysis in pp_parsed_response.analyses]
            )
            for word_analysis in pp_parsed_response.analyses:
                print(f"Generated analysis for word: {word_analysis.word}")
                print(word_analysis)

            print(
                f"{type(pp_parsed_response[0].context.comparisons)=}: {pp_parsed_response[0].context.comparisons}"
            )
            print("-" * 80)
        except Exception as e:
            print(
                f"Er is een fout opgetreden bij het verwerken van de response: {e}"
            )
            raise e

    return AnalysisResult(analyses=analyses)


def generate_recall_prompts(word_list: list[str]) -> HerinneringsTest:
    """Generates recall questions for a list of Dutch words using the Gemini API.

    Parameters
    ----------
    word_list : list[str]
        A list of Dutch words to generate recall prompts for.

    Returns
    -------
    HerinneringsTest
        A HerinneringsTest object containing the generated recall prompts.
    """
    if not word_list:
        return HerinneringsTest(gegenereerde_prompts=[])

    client = genai.Client(
        api_key=st.session_state["parameters"].gemini_api_key)

    chunk_generator = chunk_list(
        word_list, st.session_state["parameters"].recall_chunk_size)

    questions: list[TermPrompts] = []

    for chunk in chunk_generator:
        prompt = ", ".join(chunk)
        try:
            response = client.models.generate_content(
                model=st.session_state["parameters"].gemini_model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": HerinneringsTest,
                    "system_instruction": st.session_state["parameters"].recall_generation_instruction,
                },
            )
        except Exception as e:
            print(
                f"Er is een fout opgetreden bij het genereren van de recall prompts: {e}"
            )
            return HerinneringsTest(gegenereerde_prompts=[])

        # Ensure parsed_response is a HerinneringsTest instance
        if isinstance(response.parsed, HerinneringsTest):
            parsed_response = response.parsed
        else:
            raise TypeError(
                f"Unexpected response type: {type(response.parsed)}")
        questions.extend(parsed_response.gegenereerde_prompts)

    return HerinneringsTest(gegenereerde_prompts=questions)
