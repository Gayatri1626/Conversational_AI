# response_analyzer.py

from LLM.gemini_client import GeminiClient

gemini = GeminiClient()

def assess_response_quality(text):
    """
    Ask Gemini to evaluate the quality of the candidate's response.
    Returns: 'low', 'medium', or 'high'
    """
    prompt = f"""
You are a professional interview assistant.

Evaluate the following candidate response and classify its quality as:
- low (vague or incomplete)
- medium (partially explained)
- high (detailed, specific, technically sound)

Response:
\"\"\"{text}\"\"\"

Return ONLY one of these words: low, medium, or high.
"""
    response = gemini.model.generate_content(prompt)
    return response.text.strip().lower()

def adjust_difficulty_level(current_level, response_quality):
    """
    Escalates or reduces difficulty level based on the response quality.
    """
    levels = ["easy", "medium", "hard"]
    index = levels.index(current_level)

    if response_quality == "high" and index < 2:
        return levels[index + 1]
    elif response_quality == "low" and index > 0:
        return levels[index - 1]
    return current_level
