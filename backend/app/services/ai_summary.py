from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_ai_summary(player_name: str, position: str, draft_score: float, stats: dict) -> str | None:
    prompt = f"""You are a fantasy baseball analyst writing a short scouting summary.

Player: {player_name}
Position: {position}
Draft score: {draft_score:.2f} (0-1 scale, higher is better)
Recent stats: {stats}

Search for any recent injury news, surgeries, or recovery timelines for this player 
that could affect his upcoming season. Then write a 2-3 sentence qualitative summary 
of his fantasy value, highlighting key strengths, notable weaknesses, and mentioning 
any relevant injury context that explains a slow start or reduced role. Keep it concise 
and conversational, like a scouting report."""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )
        return response.text
    except Exception as e:
        print(f"AI summary generation failed for {player_name}: {e}")
        return None