# safety_filter.py

def handle_inappropriate_response(count):
    if count == 1:
        return (
            "Thank you for your response. Let's keep the conversation professional. "
            "Could you please describe a recent project you're proud of?"
        )
    elif count == 2:
        return (
            "I appreciate your participation, but please remember this is a professional interview. "
            "Another inappropriate comment will result in ending the session. Let's continue."
        )
    elif count >= 3:
        return (
            "Due to repeated unprofessional responses, I have to end the interview here. "
            "Thank you for your time."
        )

# 🧠 Gemini-based classifier (passed client from main or GeminiClient)
def is_inappropriate_with_llm(text, gemini_client):
    prompt = f"""
You are an AI assistant reviewing candidate responses in a professional interview.

Classify the following response as:
- inappropriate (if it contains rude, unprofessional, disrespectful, or offensive language),
- or appropriate (if it is respectful and interview-relevant).

Response:
\"\"\"{text}\"\"\"

Only respond with: inappropriate or appropriate.
"""
    result = gemini_client.model.generate_content(prompt)
    return result.text.strip().lower() == "inappropriate"

# 🧭 Optional: Used by GeminiClient if it decides to redirect using a polite tone
def get_filter_instruction(user_input):
    return f"""
The candidate responded inappropriately: "{user_input}"

As an AI interviewer, maintain a formal and respectful tone.
Do not react emotionally or confront the candidate.
Instead, respond with professionalism, and either:
- redirect to a relevant interview topic
- or politely remind the candidate about interview decorum.
"""
