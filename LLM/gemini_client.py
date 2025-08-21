import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from LLM.safety_filter import is_inappropriate_with_llm, get_filter_instruction
from code_reviewer.code_reviewer import analyze_python_file, fingerprint_file, compare_similarity

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiClient:
    def __init__(self, model="models/gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model)

    def ask_with_context_and_emotion(
        self,
        user_input: str,
        context_list: list,
        difficulty: str,
        emotion_blob: dict,
        code_review_path: str = None,
        solution_path: str = None
    ) -> str:
        """
        Returns ONE string:
        <empathetic-acknowledgement sentence>\n<follow-up question>
        """

        # 🔒 Safety filter
        if is_inappropriate_with_llm(user_input, self):
            return get_filter_instruction(user_input)

        # ✅ If candidate just submitted code, and we want to do code feedback follow-up
        if code_review_path and solution_path:
            try:
                review = analyze_python_file(code_review_path)
                fp1 = fingerprint_file(code_review_path)
                fp2 = fingerprint_file(solution_path)
                similarity_score = compare_similarity(fp1, fp2)
            except Exception as e:
                return f"Sorry, I encountered an error while reviewing the code: {str(e)}"

            prompt = f"""
You are an AI interviewer.

Here is the candidate's code review summary:
{json.dumps(review, indent=2)}

The code has {similarity_score * 100:.1f}% similarity with a known correct solution.

Ask ONE insightful follow-up question about their approach or reasoning.
"""
            response = self.model.generate_content(prompt)
            return response.text.strip()

        # 💬 Build examples block
        examples_block = "\n".join(
            f"- Q: {c['text'].split('A:')[0].strip()}\n  A: {c['text'].split('A:')[1].strip()}\n  Follow-up: {c.get('next_question','')}"
            for c in context_list if "text" in c and "A:" in c['text']
        )

        # 😌 Emotion context
        dom = emotion_blob.get("dominant", "neutral")
        stress = emotion_blob.get("stress_score", 0)

        # 🤖 Prompt for regular conversation
        prompt = f"""
You are VIKA, an expert technical interviewer with excellent emotional intelligence.

* Candidate dominant emotion   : **{dom}**
* Estimated stress (0‑1 scale) : **{stress:.2f}**
* Next question difficulty     : **{difficulty}**

TASK
-----
1. First, in ≤25 words, acknowledge the candidate's emotion politely **and** keep them motivated.
2. THEN on a new line, ask ONE follow-up question of <{difficulty}> difficulty that probes their skills.
3. Do **not** add any extra preamble or labels.

Context examples:
{examples_block}

Candidate just said:
\"\"\"{user_input}\"\"\"
"""
        resp = self.model.generate_content(prompt)
        return resp.text.strip()
