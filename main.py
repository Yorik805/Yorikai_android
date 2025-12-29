# main.py
from fastapi import FastAPI, Request
import google.generativeai as genai
import random
import asyncio
import httpx

SYSTEM_INSTRUCTIONS = """
You are a personal AI assistant used by a user for studying, chatting, and help.
- Reply explicitly in JSON structure, exactly like this:
  [
      {"type":"speak"},
      {"speech":"the speech goes here without stars"}
  ]
- The user may use STT, which could have errors.
- If you encounter a nonsensical or grammatical sentence, make a reasonable assumption and ask the user to confirm.
- Keep tone friendly, not too formal, not too casual.
"""

# Configure Gemini
genai.configure(api_key="AIzaSyCn7ScApahWSAASklQE_AYi2Xv2ZMs-ZsY")
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=SYSTEM_INSTRUCTIONS
)

# FastAPI setup
app = FastAPI()

# Random filler sentences
RANDOM_SENTENCES = [
    "Hey, I am just checking in!",
    "Do you want to continue studying?",
    "Remember to take a short break!",
]

# /gemini endpoint: returns a random sentence
@app.get("/gemini")
async def gemini_random():
    sentence = random.choice(RANDOM_SENTENCES)
    return {"sentence": sentence}

# /call_gemini endpoint: calls Gemini API
@app.post("/call_gemini")
async def call_gemini(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")

    try:
        # Direct call (no async streaming)
        response = model.generate_content(user_prompt)
        full_reply = response.text  # Gemini returns JSON string
    except Exception as e:
        return {"error": str(e)}

    # Forward Gemini JSON as-is
    import json
    try:
        json_reply = json.loads(full_reply)
    except Exception:
        json_reply = {"error": "Invalid JSON from Gemini", "raw": full_reply}

    return json_reply


    # Gemini itself is sending JSON, so forward it as-is
    # Parse string to dict if necessary
    import json
    try:
        json_reply = json.loads(full_reply)
    except Exception:
        json_reply = {"error": "Invalid JSON from Gemini", "raw": full_reply}

    return json_reply

# # Optional: background sender for random /gemini triggers
# async def random_sender():
#     while True:
#         try:
#             async with httpx.AsyncClient() as client:
#                 await client.get("http://localhost:1234/gemini")
#         except Exception:
#             pass
#         await asyncio.sleep(random.randint(60, 300))  # 1-5 minutes

# # Start background sender when app starts
# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(random_sender())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1234)

    # ------------------------ TABLET MODE ------------------------
    # Uncomment the lines below when running locally on your tablet
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=1234)
