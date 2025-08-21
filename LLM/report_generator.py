# report_generator.py
"""
Generate a comprehensive, emotion‑aware post‑interview report.

Usage:
    from report_generator import generate_interview_report
    report_md = generate_interview_report(conversation_log, gemini)
"""

import json

def generate_interview_report(conversation_log, gemini_client):
    """
    Args
    ----
    conversation_log : list[dict]
        The full log collected during the session (VIKA, Candidate, EMOTION, etc.).
    gemini_client    : GeminiClient
        Your already‑configured Gemini wrapper; we’ll reuse its .model.

    Returns
    -------
    report_markdown : str
        A nicely formatted Markdown report.
    """
    prompt = f"""
You are VIKA‑Report, an AI assistant that generates post‑interview evaluations.

Below is a structured JSON list capturing an AI‑driven interview.  
Each entry may contain:
  • "speaker": "VIKA" | "Candidate" | "EMOTION"
  • "text":   (for VIKA/Candidate turns)
  • "data":   (for EMOTION blobs with dominant/stress_score)

TASKS
1. Summarize the candidate's emotional progression (calm, nervous, improving?).
2. Assess professionalism and technical depth of answers (low/medium/high).
3. Comment on how VIKA adapted question difficulty or tone.
4. Give a final verdict: **Strongly Recommend / Recommend / Neutral / Not Recommend** – explain why in ≤ 3 bullet points.

Respond in clear Markdown using headings (##) and bullet lists where helpful.

JSON LOG:
{json.dumps(conversation_log, indent=2)}
"""

    response = gemini_client.model.generate_content(prompt)
    return response.text.strip()
