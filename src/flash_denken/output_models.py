'''This module defines the data models for the structured word analysis API.'''

import re
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from pydantic.main import TupleGenerator


class StringToStringDict(Dict[str, str]):
    """A custom Pydantic model that represents a dictionary where both keys and values are strings.
    This is used to handle the comparisons field in the ContextualInfo model.
    It ensures that the dictionary adheres to the expected format and can be serialized/deserialized correctly.
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        # This tells Pydantic's core schema generator to treat it like a dictionary where values are strings.
        # This method is primarily for Pydantic's internal validation, not directly for JSON schema generation.
        return handler(str)

    @classmethod
    def model_json_schema(cls, **kwargs):
        # This is crucial for the JSON schema that gets sent to the API.
        # We manually define it to ensure it only contains 'type: object' and 'patternProperties'.
        # This avoids the 'additionalProperties' error.
        return {
            "type": "object",
            "title": "StringToStringDict",
            "description": "A dictionary where keys and values are both strings.",
            "patternProperties": {
                ".*": {"type": "string"}
            }
        }


class CoreMeaning(BaseModel):
    """Describes the fundamental meaning and nuance of the word."""
    translation: List[str] = Field(
        ..., description="A list of common English translations.")
    nuance: str = Field(
        ..., description="A detailed explanation of the word's specific flavor, intensity, and connotations.")

    def __str__(self):
        """Returns a string representation of the core meaning."""
        return f"CoreMeaning(translation={self.translation}, nuance={self.nuance})"

    def __len__(self):
        """Returns the number of translations in the core meaning."""
        return len(self.translation)

    def __getitem__(self, index: int) -> str:
        """Allows indexing into the translation list."""
        if 0 <= index < len(self.translation):
            return self.translation[index]
        raise IndexError("Index out of range for translation list")


class ContextualInfo(BaseModel):
    """Describes how the word is used in different contexts."""
    formality: str = Field(
        ..., description="The typical formality level (e.g., 'Informal', 'Formal', 'Neutral').")
    comparisons: StringToStringDict = Field(
        ..., description="A dictionary comparing the word to its close synonyms, explaining the subtle differences in usage and feeling.")
    typical_usage: str = Field(
        ..., description="A brief description of the contexts where this word is most often found (e.g., 'academic writing', 'spoken language with friends').")
    common_mistake: Optional[str] = Field(
        None, description="A common mistake or a 'near miss' scenario where a learner might incorrectly use this word. Explain why it's wrong.")

    def __str__(self):
        """Returns a string representation of the contextual information."""
        return f"ContextualInfo(formality={self.formality}, typical_usage={self.typical_usage}, common_mistake={self.common_mistake}, comparisons={self.comparisons})"

    def __len__(self):
        """Returns the number of comparisons in the contextual info."""
        return len(self.comparisons)

    def __getitem__(self, key: str) -> str:
        """Allows accessing comparisons by their keys."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in ContextualInfo")


class RelationalWeb(BaseModel):
    """Maps the word's connections to other words."""
    synonyms: List[str] = Field(
        ..., description="A list of words with similar meanings.")
    antonyms: List[str] = Field(
        ..., description="A list of words with opposite meanings.")
    collocations: List[str] = Field(
        ..., description="Common fixed expressions or collocations where this word is used. E.g., for 'beslissing', a good entry would be 'een beslissing nemen'.")

    def __str__(self):
        """Returns a string representation of the relational web."""
        return f"RelationalWeb(synonyms={self.synonyms}, antonyms={self.antonyms}, collocations={self.collocations})"

    def __len__(self):
        """Returns the total number of related words (synonyms + antonyms + collocations)."""
        return len(self.synonyms) + len(self.antonyms) + len(self.collocations)

    def __getitem__(self, key: str) -> List[str]:
        """Allows accessing synonyms or antonyms by their names."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in RelationalWeb")


class Physicality(BaseModel):
    """Describes the sound and structure of the word."""
    pronunciation_ipa: str = Field(
        ..., description="The pronunciation using the International Phonetic Alphabet (IPA).")

    def __str__(self):
        """Returns a string representation of the physicality."""
        return f"Physicality(pronunciation_ipa={self.pronunciation_ipa}, pronunciation_simple={self.pronunciation_simple})"

    def __len__(self):
        """Returns the length of the pronunciation in IPA."""
        return len(self.pronunciation_ipa)

    def __getitem__(self, key: str) -> str:
        """Allows accessing fields by their names."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in Physicality")


class ThoughtScenario(BaseModel):
    """A narrative scenario that creates the need for the word, simulating how a native speaker would think."""
    title: str = Field(...,
                       description="A short, descriptive title for the scenario.")
    situation: str = Field(...,
                           description="The objective facts of the mini-story.")
    internal_monologue: str = Field(
        ..., description="The pre-linguistic internal thought, judgment, or feeling of the character in the story.")
    expression: str = Field(
        ..., description="The final articulated sentences in Dutch, where the target word emerges as the natural choice. The target word should be enclosed in **double asterisks**.")

    def __str__(self):
        """Returns a string representation of the thought scenario."""
        return f"ThoughtScenario(title={self.title}, situation={self.situation})"

    def __len__(self):
        """Returns the length of the internal monologue."""
        return len(self.internal_monologue)

    def __getitem__(self, key: str) -> str:
        """Allows accessing fields by their names."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in ThoughtScenario")


class WordAnalysis(BaseModel):
    """The complete, structured analysis for a single word."""
    word: str = Field(...,
                      description="The Dutch word being analyzed.")
    part_of_speech: str = Field(
        ..., description="The grammatical part of speech (e.g., 'Adverb', 'Verb', 'Adjective').")
    definition: str = Field(...,
                            description="A concise definition of the word")
    article: str = Field(
        ..., description="The definite article for the word, if applicable (e.g., 'de', 'het').")
    simple_past: str = Field(
        ..., description="The simple past form of the verb, if applicable.")
    past_participle: str = Field(
        ..., description="The past participle form of the verb, if applicable.")
    meaning: CoreMeaning
    context: ContextualInfo
    relations: RelationalWeb
    physicality: Physicality
    thought_scenarios: List[ThoughtScenario] = Field(...,
                                                     description="At least three distinct thought scenarios demonstrating the word's use. The third one with an empty `expression` field to allow the user to fill it in later."
                                                     )

    def __str__(self):
        """Returns a string representation of the word analysis."""
        return f"WordAnalysis(word={self.word}, part_of_speech={self.part_of_speech})"

    def __len__(self):
        """Returns the number of thought scenarios in the analysis."""
        return len(self.thought_scenarios)

    def __getitem__(self, key: str) -> BaseModel:
        """Allows accessing nested models by their field names."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in WordAnalysis")


class AnalysisResult(BaseModel):
    """The root model for the entire API response, containing a list of analyses."""
    analyses: List[WordAnalysis]

    def __len__(self):
        """Returns the number of analyses in the result."""
        return len(self.analyses)

    def __getitem__(self, index: int) -> WordAnalysis:
        """Allows indexing into the analyses list."""
        return self.analyses[index]


# an extended WordAnalysis, to contain image, video, audio path/url

class ExtendedWordAnalysis(WordAnalysis):
    """An extended version of WordAnalysis to include media paths/URLs."""
    user_media: List[Dict[str, str]] = Field(...,
                                             description="A list of media associated with the word, including images, videos, and audio.")


class EnkelePrompt(BaseModel):
    """Represents a single recall prompt for a specific term, categorized by creative type."""
    categorie: str = Field(..., description="The creative category of the prompt. Must be one of: 'SLICE_OF_LIFE', 'PROBLEM_SOLUTION', 'SENSORY_EMOTIONAL', 'LOGISCHE_AFLEIDING'.")
    prompt_tekst: str = Field(
        ..., description="The situational prompt text in Dutch, designed to elicit the 'doel_antwoord' from the user's memory.")
    doel_antwoord: str = Field(
        ..., description="The target Dutch term (word or phrase) that the user is expected to recall based on the 'prompt_tekst'.")

    def __str__(self) -> str:
        return f"Categorie: {self.categorie}\nPrompt: {self.prompt_tekst}\nDoel Antwoord: {self.doel_antwoord}"


class TermPrompts(BaseModel):
    """Contains a set of prompts for a specific term, ensuring that each prompt is from a different creative category."""
    term: str = Field(..., description="The original Dutch term from the input for which the prompts were generated.")
    prompts: List[EnkelePrompt] = Field(
        ..., description="A list containing exactly four distinct recall prompts for the 'term', each from a different category.")

    def __len__(self):
        return len(self.prompts)

    def __getitem__(self, index: int):
        return self.prompts[index]

    def __str__(self) -> str:
        message = f"Term: {self.term}\n"
        for prompt in self.prompts:
            message += str(prompt)
        return message


class HerinneringsTest(BaseModel):
    """The root model for the recall test, containing a list of generated prompts for each term."""
    gegenereerde_prompts: List[TermPrompts] = Field(
        ..., description="A list of generated prompt sets, one for each term provided in the input.")

    def __len__(self):
        return len(self.gegenereerde_prompts)

    def __getitem__(self, index: int):
        return self.gegenereerde_prompts[index]

    def __str__(self) -> str:
        message = "Herinnerings Test Prompts:\n"
        for term_prompts in self.gegenereerde_prompts:
            message += str(term_prompts) + "\n"
        return message
