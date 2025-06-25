
import re
from typing import List, Optional
from output_models import (
    WordAnalysis, CoreMeaning, ContextualInfo, RelationalWeb, Physicality,
    ThoughtScenario, EnkelePrompt
)


def _generate_css() -> str:
    """Generates the main CSS styles for the HTML page, infused with a subtle Dutch touch and playful, soul-pleasing aesthetics."""
    return """
        :root {
            /* Revised Color Palette: Softer, more inviting, a bit more Dutch landscape-inspired */
            --primary-text-color: #2C3E50; /* Darker blue-grey for main text - professional yet warm */
            --secondary-text-color: #7F8C8D; /* Muted grey for supporting info - soft, earthy */
            --background-color-light: #FBFBFB; /* Very light, almost off-white for body background - airy, clean */
            --background-color-card: #FFFFFF; /* Pure white for main content cards - crisp contrast */
            --accent-color: #007bff; /* A slightly brighter, more vibrant Dutch blue, symbolizing clarity & opportunity */
            --secondary-accent-color: #FF7F50; /* Coral/soft orange - a playful, warm complementary color */
            --border-color: #E0E0E0; /* Lighter, softer border */
            --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); /* Slightly more prominent but still soft shadow */
            --highlight-bg-color: #F8F9FA; /* A very subtle light grey for element backgrounds, gentle */
        }

        body {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; /* Using 'Inter' (or fallback), a modern, friendly sans-serif */
            line-height: 1.8; /* Increased line-height for more breathing room */
            color: var(--primary-text-color);
            background-color: var(--background-color-light);
            /* Add a subtle background texture for depth and playfulness */
            background-image: url("data:image/svg+xml,%3Csvg width='6' height='6' viewBox='0 0 6 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23e9e9e9' fill-opacity='0.15' fill-rule='evenodd'%3E%3Cpath d='M5 0h1L0 6V5zm1 6v-1L1 0h1z'/%3E%3C/g%3E%3C/svg%3E"); /* Very subtle diagonal lines */
            margin: 0;
            padding: 60px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .word-container {
            background-color: var(--background-color-card);
            border-radius: 20px; /* Even softer rounded corners */
            box-shadow: var(--card-shadow);
            padding: 60px 70px;
            max-width: 950px;
            width: 100%;
            box-sizing: border-box;
            position: relative; /* For potential future animations */
            overflow: hidden; /* Ensures shadows/transforms are clipped */
        }

        h1 {
            font-family: 'Outfit', sans-serif; /* A clear, modern, slightly more geometric font for impact */
            color: var(--accent-color); /* H1 using accent color for vibrancy */
            font-size: 3.8em; /* Slightly larger, more dominant */
            font-weight: 700;
            margin-bottom: 5px; /* Less margin, bringing POS closer */
            display: inline-block;
            vertical-align: bottom;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.05); /* Subtle text shadow for depth */
        }

        .part-of-speech {
            font-size: 1.6em; /* A bit larger to match the H1 scale */
            color: var(--secondary-text-color);
            font-style: normal;
            font-weight: 400;
            margin-left: 20px; /* Slightly more distinct separation */
            display: inline-block;
            vertical-align: bottom;
        }

        h2 {
            font-family: 'Outfit', sans-serif; /* Consistent header font */
            color: var(--primary-text-color);
            font-size: 2.5em; /* Larger, clearer section headers */
            font-weight: 600;
            border-bottom: 2px solid var(--border-color); /* Slightly thicker, more defined border */
            padding-bottom: 15px; /* More padding */
            margin-top: 50px; /* More vertical space */
            margin-bottom: 35px; /* More vertical space */
            position: relative;
        }
        h2::after { /* A subtle, playful accent under the h2 */
            content: '';
            display: block;
            width: 50px; /* A short accent line */
            height: 4px;
            background-color: var(--secondary-accent-color); /* Using the new accent color */
            position: absolute;
            bottom: -2px; /* Position it slightly overlapping the border */
            left: 0;
            border-radius: 2px;
        }


        h3 {
            font-family: 'Outfit', sans-serif; /* Consistent header font */
            color: var(--primary-text-color);
            font-size: 2em; /* Clearer sub-headings, bolder */
            font-weight: 600;
            margin-top: 40px; /* More space */
            margin-bottom: 20px; /* More space */
        }

        p {
            margin-bottom: 1.5em; /* More space between paragraphs */
            color: var(--primary-text-color); /* Ensure paragraph text color is consistent */
        }

        ul {
            list-style: none;
            padding: 0;
            margin-bottom: 2em; /* More margin */
        }

        li {
            margin-bottom: 1.2em; /* More space between list items */
            padding-left: 2em; /* Ample space for bullet */
            position: relative;
        }
        li::before {
            content: '♦'; /* A slightly more interesting diamond bullet */
            color: var(--secondary-accent-color); /* Bullet in secondary accent color for playfulness */
            font-size: 1.1em; /* Standard size bullet */
            position: absolute;
            left: 0;
            top: 0.1em; /* Fine-tuned alignment */
            font-weight: bold;
        }

        .tag {
            background-color: var(--highlight-bg-color);
            color: var(--primary-text-color); /* Tags use primary text color for readability */
            padding: 10px 18px; /* Slightly larger, more comfortable tags */
            border-radius: 12px; /* Softer pill shape */
            font-size: 1em; /* Slightly larger font */
            font-weight: 500;
            margin-right: 15px; /* More space */
            margin-bottom: 15px; /* More space */
            display: inline-block; /* Ensure they lay out nicely */
            transition: background-color 0.3s ease, transform 0.2s ease; /* Transition for hover */
        }
        .tag:hover {
            background-color: var(--accent-color); /* Hover effect for tags */
            color: white;
            transform: translateY(-2px); /* Subtle lift on hover */
        }


        .pronunciation {
            font-family: 'Fira Mono', monospace; /* A clean, modern monospaced font */
            font-size: 1.2em; /* Slightly larger for clarity */
            background-color: var(--highlight-bg-color);
            padding: 15px 22px; /* More padding */
            border-radius: 12px;
            display: inline-block;
            margin-top: 25px;
            color: var(--primary-text-color);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05); /* Subtle shadow */
        }

        .scenario-grid {
            /* FORCED SINGLE COLUMN: All scenarios will stack vertically */
            display: grid;
            grid-template-columns: 1fr; /* This is the key: forces one column */
            gap: 40px; /* Still maintains vertical space between cards */
            margin-top: 40px; /* More space above */
        }

        .scenario-card {
            background-color: var(--background-color-card);
            border: 1px solid var(--border-color);
            border-radius: 16px; /* Softer radius */
            padding: 35px; /* More internal padding */
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06); /* Softer initial shadow */
            transition: transform 0.3s ease-out, box-shadow 0.3s ease-out; /* Smoother, longer transition */
        }
        .scenario-card:hover {
            transform: translateY(-6px) scale(1.005); /* More noticeable lift and tiny scale */
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15); /* More prominent shadow on hover */
        }

        .scenario-card h4 {
            font-family: 'Outfit', sans-serif; /* Consistent header font */
            color: var(--accent-color); /* Scenario titles use accent color */
            font-size: 1.6em; /* Clearer scenario titles */
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 18px; /* More margin */
        }

        .scenario-card p {
            margin-bottom: 1.2em;
            font-size: 1.05em; /* Slightly larger text in cards for readability */
            color: var(--secondary-text-color); /* Card text a bit softer */
        }

        .scenario-card .label {
            font-weight: 700; /* Labels even bolder */
            color: var(--primary-text-color);
            margin-right: 12px; /* More space */
        }

        .comparison-item {
            margin-bottom: 30px; /* More space */
            padding-bottom: 30px;
            border-bottom: 1px dashed var(--border-color); /* Dashed border for a lighter, more playful feel */
        }
        .comparison-item strong {
            color: var(--primary-text-color);
            font-weight: 700; /* Even bolder */
            font-size: 1.25em; /* Clearer comparison headings */
        }

        .expression-text {
            font-weight: 500;
            color: var(--primary-text-color);
            background-color: var(--highlight-bg-color);
            padding: 18px 25px; /* More padding for a softer feel */
            border-radius: 14px; /* Softer radius */
            display: block;
            margin-top: 30px; /* More space */
            font-style: italic; /* Subtle italic for expressions, makes them feel distinct */
            box-shadow: inset 0 1px 5px rgba(0,0,0,0.03); /* Inner shadow for subtle depth */
        }
        .expression-text strong {
            color: var(--accent-color); /* The core word accent color */
            font-weight: 800; /* Extra bold for emphasis */
            /* animation: pulse 1.5s infinite alternate; /* Uncomment for continuous subtle pulse */
        }

        /* Keyframes for potential subtle pulse animation on highlighted words */
        @keyframes pulse {
            from { transform: scale(1); }
            to { transform: scale(1.01); }
        }

        /* --- New CSS for user-added sections --- */
        .user-added-section {
            margin-top: 60px; /* More space above this whole section */
            padding-top: 30px;
            border-top: 2px solid var(--secondary-accent-color); /* A clear divider */
        }

        .user-added-section h2 {
            color: var(--secondary-accent-color); /* Make this section's header stand out */
            border-color: var(--accent-color); /* Complementary border */
        }
        .user-added-section h2::after {
            background-color: var(--primary-text-color); /* A different accent for this H2 */
        }

        .user-scenario-card h4 {
            color: var(--accent-color); /* Keep scenario titles consistent */
        }

        .user-media-card {
            text-align: center;
            margin-top: 40px; /* Space between user scenario and media */
        }
        .user-media-card img,
        .user-media-card video,
        .user-media-card audio {
            max-width: 100%;
            width: 80%; /* Make media a bit narrower for better focus */
            min-height: 50px; /* Ensure there's a minimum height for media */
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Subtle shadow for media */
        }
        .user-media-card video {
            max-height: 400px; /* Limit video height */
        }
        .user-media-card audio {
            width: 80%; /* Make audio player a bit narrower */
        }

        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700&family=Fira+Mono:wght@400&display=swap');
    """


def _generate_header_html(analysis: 'WordAnalysis') -> str:
    """Generates the main word and part of speech header."""
    return f"""
        <h1>{analysis.word}</h1>
        <span class="part-of-speech">({analysis.part_of_speech})</span>
        <p class="definition">{analysis.definition}</p>
    """


def _generate_core_meaning_html(meaning: 'CoreMeaning') -> str:
    """Generates the HTML for the Core Meaning section with Dutch subheaders."""
    translations_html = "".join(f"<li>{t}</li>" for t in meaning.translation)
    return f"""
        <h2>Kernbetekenis</h2>
        <h3>Vertalingen</h3>
        <ul>
            {translations_html}
        </ul>
        <h3>Nuance</h3>
        <p>{meaning.nuance}</p>
    """


def _generate_grammar_html(analysis: 'WordAnalysis') -> str:
    """Generates the HTML for the Grammar section with Dutch subheaders."""
    return f"""
        <h2>Grammatica</h2>
        <p><span class="label">Lidwoord:</span> {analysis.article}</p>
        <p><span class="label">Verleden Tijd:</span> {analysis.simple_past}</p>
        <p><span class="label">Voltooid Deelwoord:</span> {analysis.past_participle}</p>
    """


def _generate_contextual_info_html(context: 'ContextualInfo') -> str:
    """Generates the HTML for the Contextual Information section with Dutch subheaders."""
    comparisons_html = ""
    if context.comparisons:
        for synonym, explanation in context.comparisons.items():
            comparisons_html += f"""
            <div class="comparison-item">
                <strong>{synonym}</strong>: {explanation}
            </div>
            """
    else:
        comparisons_html = "<p>Geen specifieke vergelijkingen beschikbaar.</p>"

    return f"""
        <h2>Contextuele Informatie</h2>
        <p><span class="label">Formaliteit:</span> <span class="tag">{context.formality}</span></p>
        <h3>Typisch Gebruik</h3>
        <p>{context.typical_usage}</p>
        <h3>Veelgemaakte Fouten</h3>
        <p>{context.common_mistake}</p>
        <h3>Vergelijkingen</h3>
        {comparisons_html}
    """


def _generate_relational_web_html(relations: 'RelationalWeb') -> str:
    """Generates the HTML for the Relational Web section with Dutch subheaders."""
    synonyms_html = "".join(
        f'<span class="tag">{s}</span>' for s in relations.synonyms) if relations.synonyms else "Geen synoniemen beschikbaar."
    antonyms_html = "".join(
        f'<span class="tag">{a}</span>' for a in relations.antonyms) if relations.antonyms else "Geen antoniemen beschikbaar."
    collocations_html = "".join(
        f'<span class="tag">{c}</span>' for c in relations.collocations) if relations.collocations else "Geen collocaties beschikbaar."

    return f"""
        <h2>Relationeel Netwerk</h2>
        <h3>Synoniemen</h3>
        <p>{synonyms_html}</p>
        <h3>Antoniemen</h3>
        <p>{antonyms_html}</p>
        <h3>Collocaties</h3>
        <p>{collocations_html}</p>
    """


def _generate_physicality_html(physicality: 'Physicality') -> str:
    """Generates the HTML for the Physicality section with Dutch subheaders."""
    return f"""
        <h2>Uitspraak & Vorm</h2>
        <h3>Uitspraak (IPA)</h3>
        <p class="pronunciation">{physicality.pronunciation_ipa}</p>
    """


def _generate_scenarios_html(scenarios: List['ThoughtScenario'], target_word: str) -> str:
    """
    Generates the HTML for the Thought Scenarios section with Dutch subheaders,
    ensuring the target word is consistently highlighted.
    """
    scenarios_cards_html = ""
    for scenario in scenarios:
        # First, remove any existing '**' markers from the expression to prevent conflicts
        # with our new automatic highlighting logic.
        cleaned_expression = scenario.expression.replace('**', '')

        # Highlight the target_word (analysis.word) within the cleaned expression.
        # This regex performs a case-insensitive replacement of the exact word, respecting word boundaries.
        # It replaces the matched text with the target word wrapped in strong tags.
        highlighted_expression = re.sub(
            # Escape special regex characters in target_word
            r'\b' + re.escape(target_word) + r'\b',
            # Replace with the target word wrapped in strong
            f'<strong>{target_word}</strong>',
            cleaned_expression,
            flags=re.IGNORECASE
        )

        if highlighted_expression:
            scenarios_cards_html += f"""
                <div class="scenario-card">
                    <h4>{scenario.title}</h4>
                    <p><span class="label">Situatie:</span> {scenario.situation}</p>
                    <p><span class="label">Interne Monoloog:</span> {scenario.internal_monologue}</p>
                    <div class="expression-text">
                        <span class="label">Uitdrukking:</span> {highlighted_expression}
                    </div>
                </div>
            """
        else:  # put an input field for the user to fill in
            scenarios_cards_html += f"""
                <div class="scenario-card">
                    <h4>{scenario.title}</h4>
                    <p><span class="label">Situatie:</span> {scenario.situation}</p>
                    <p><span class="label">Interne Monoloog:</span> {scenario.internal_monologue}</p>
                    <div class="expression-text">
                        <span class="label">Uitdrukking:</span>
                        <input type="text" placeholder="Vul hier de uitdrukking in met '{target_word}'" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color);">
                    </div>
                </div>
            """
    return f"""
        <h2>Gedachtescenario's</h2>
        <div class="scenario-grid">
            {scenarios_cards_html}
        </div>
    """


def _generate_user_scenario_html(user_scenario: 'ThoughtScenario', target_word: str) -> str:
    """Generates HTML for a single user-provided thought scenario."""
    # Ensure user-provided scenario's expression also highlights the target word
    cleaned_expression = user_scenario.expression.replace('**', '')
    highlighted_expression = re.sub(
        r'\b' + re.escape(target_word) + r'\b',
        f'<strong>{target_word}</strong>',
        cleaned_expression,
        flags=re.IGNORECASE
    )

    statement = f"""
        <div class="user-added-section">
            <h2>Jouw Eigen Gedachtescenario</h2>
            <div class="scenario-grid">
                <div class="scenario-card user-scenario-card">
                    <h4>{user_scenario.title}</h4>
                    <p><span class="label">Situatie:</span> {user_scenario.situation}</p>
                    <p><span class="label">Interne Monoloog:</span> {user_scenario.internal_monologue}</p>
                    <div class="expression-text">
                        <span class="label">Uitdrukking:</span> {highlighted_expression}
                    </div>
                </div>
            </div>
        </div>
    """

    return statement


def _generate_user_media_html(image_url: Optional[str] = None,
                              audio_url: Optional[str] = None,
                              video_url: Optional[str] = None) -> str:
    """Generates HTML for user-provided media (image, audio, video)."""
    media_content = []
    if image_url:
        media_content.append(
            f'<img src="{image_url}" alt="Door gebruiker toegevoegde afbeelding">')
    if audio_url:
        media_content.append(f"""
            <audio controls>
                <source src="{audio_url}" type="audio/mpeg">
                <source src="{audio_url}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        """)
    if video_url:
        media_content.append(f"""
            <video controls>
                <source src="{video_url}" type="video/mp4">
                <source src="{video_url}" type="video/webm">
                Your browser does not support the video tag.
            </video>
        """)

    if not media_content:
        return ""  # Return empty string if no media is provided

    return f"""
        <div class="user-added-section user-media-card">
            <h2>Jouw Eigen Media</h2>
            {"".join(media_content)}
        </div>
    """


def generate_word_html_design(
    analysis: 'WordAnalysis',
    user_scenario: Optional['ThoughtScenario'] = None,
    user_image_url: Optional[str] = None,
    user_audio_url: Optional[str] = None,
    user_video_url: Optional[str] = None
) -> str:
    """
    Generates a beautiful HTML/CSS design for a given WordAnalysis object,
    with Dutch subheaders and consistent highlighting, and translation at the end.
    Optionally includes user-provided scenarios and media.

    Args:
        analysis: A Pydantic WordAnalysis object containing all word details.
        user_scenario: An optional ThoughtScenario object provided by the user.
        user_image_url: An optional URL for a user-provided image.
        user_audio_url: An optional URL for a user-provided audio file.
        user_video_url: An optional URL for a user-provided video file.

    Returns:
        A string containing the full HTML document with embedded CSS.
    """
    css_content = _generate_css()
    header_html = _generate_header_html(analysis)
    grammar_html = _generate_grammar_html(analysis)
    contextual_info_html = _generate_contextual_info_html(analysis.context)
    relational_web_html = _generate_relational_web_html(analysis.relations)
    physicality_html = _generate_physicality_html(analysis.physicality)
    scenarios_html = _generate_scenarios_html(
        analysis.thought_scenarios, analysis.word)
    core_meaning_html = _generate_core_meaning_html(analysis.meaning)

    # Conditional generation of user-provided content
    user_content_html = ""
    if user_scenario:
        user_content_html += _generate_user_scenario_html(
            user_scenario, analysis.word)

    # Combine all media into one section if any is provided
    if user_image_url or user_audio_url or user_video_url:
        user_content_html += _generate_user_media_html(
            user_image_url, user_audio_url, user_video_url)

    html_template = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Woordanalyse: {analysis.word}</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    <div class="word-container">
        {header_html}
        {grammar_html}
        {contextual_info_html}
        {relational_web_html}
        {physicality_html}
        {scenarios_html}
        {core_meaning_html}
        {user_content_html} </div>
</body>
</html>
    """
    return html_template


# embed for streamlit, use iframe
def embed_video(video_url: str) -> str:
    """Generates an HTML iframe for embedding a video in Streamlit.
    Parameters
    ----------
        video_url: The URL of the video to embed
    Returns
    -------
        A string containing the HTML iframe code for the video.
    """
    return f"""
    <iframe width="80%" height="500" src="{video_url}" frameborder="0" allowfullscreen></iframe>
    """


def generate_single_prompt_card_html(prompt: EnkelePrompt) -> str:
    """
    Genereert gestileerde HTML voor een enkele leertip (prompt_tekst)
    met ingebedde CSS voor een zelfstandige weergave. De styling is
    verbeterd om de prompt prominenter en 'op een voetstuk' te plaatsen,
    zonder de dubbele aanhalingstekens.

    Args:
        prompt: Een EnkelePrompt-object dat de promptdetails bevat.

    Returns:
        Een string met de gestileerde HTML voor één promptkaart,
        inclusief alle benodigde styling.
    """
    if not isinstance(prompt, EnkelePrompt):
        # Fallback for unexpected input type
        return "<p style='color: red; font-family: sans-serif;'>Fout: Verwacht een EnkelePrompt object als invoer.</p>"

    # Remove quotes if they are part of the input string
    cleaned_prompt_text = prompt.prompt_tekst.strip('"')

    # HTML for a single prompt card with embedded <style> for self-contained styling
    html_content = f"""
    <div style="
        background-color: #e8f0fe; /* A slightly more vibrant light blue background */
        background: linear-gradient(145deg, #e0efff, #d5e9ff); /* Subtle gradient for depth */
        border: 2px solid #8ba8cd; /* Thicker, more distinct border */
        border-radius: 20px; /* Even more rounded corners */
        padding: 40px; /* Increased padding to give it more 'mass' */
        margin-bottom: 30px; /* Consistent spacing */
        /* Enhanced box-shadow for a 'pedestal' effect, with a subtle blue glow */
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15), 0 0 0 4px rgba(100, 150, 250, 0.2);
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        font-family: 'Inter', sans-serif; /* Fallback to generic sans-serif */
        box-sizing: border-box;
        position: relative; /* Needed for potential future pseudo-elements */
        overflow: hidden; /* Ensures content stays within rounded corners */
        max-width: 750px; /* Slightly wider to accommodate larger text */
        margin-left: auto; /* Center the div */
        margin-right: auto; /* Center the div */
    "
    onmouseover="this.style.transform='translateY(-10px)'; this.style.boxShadow='0 20px 45px rgba(0,0,0,0.25), 0 0 0 6px rgba(120, 180, 255, 0.3)'; cursor: pointer;"
    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 15px 35px rgba(0,0,0,0.15), 0 0 0 4px rgba(100, 150, 250, 0.2)';">
        <style>
            /* Embed a local style for the prompt text */
            .prompt-text-embedded {{
                font-size: 1.4rem; /* Even larger font size for prominence */
                line-height: 1.8; /* Improved line height for readability */
                color: #2c3e50; /* Darker, more prominent text color */
                font-weight: 600; /* Semi-bold font weight to truly stand out */
                margin: 0; /* Remove default paragraph margins */
                text-align: center; /* Center align the text */
            }}
            /* Import Google Font if not already loaded globally in Streamlit */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        </style>
        <p class="prompt-text-embedded">{cleaned_prompt_text}</p>
    </div>
    """
    return html_content
