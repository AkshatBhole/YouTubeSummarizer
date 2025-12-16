import sys
import os
import time
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


app = Flask(__name__)
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "Backend is running",
        "service": "YouTube AI Analyzer",
        "endpoints": ["/api/analyze"]
    })

CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS"])

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response



load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)


def extract_video_id(url):
    """Simple helper to extract video ID from URL"""
    if not url: return None
    # Handle common formats
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    if "/live/" in url:
        return url.split("/live/")[1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    # Fallback for shorts just in case
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]
    return None

# --- Layer 1: Native & Auto-Generated Captions ---
def _get_native_transcript(video_id):
    api = YouTubeTranscriptApi()
    
    # Method A: Direct Fetch
    try:
        print(f"[Layer 1] Trying api.fetch for {video_id}...")
        transcript_json = api.fetch(video_id)
        return _parse_transcript_result(transcript_json)
    except Exception as e:
        print(f"[Layer 1] api.fetch failed: {e}")

    # Method B: List & Search
    try:
        print(f"[Layer 1] Falling back to api.list for {video_id}...")
        transcript_list = api.list(video_id)
        # transcript_list is likely an iterable of Transcript objects
        for t in transcript_list:
            # We just take the first one found (often auto-generated English)
            print(f"[Layer 1] Found transcript: {t}")
            # Ensure we can fetch it
            # The transcript object usually has a .fetch() method in standard lib,
            # or we might need to use api.fetch(video_id, languages=[t.language_code])?
            # Let's try calling fetch on the object itself if it exists
            if hasattr(t, 'fetch'):
                 return _parse_transcript_result(t.fetch())
            
            # If not, maybe we can use the main api with language param?
            # But earlier debug showed fetch() takes no language param in this weird version?
            # Let's rely on the object's fetch if possible.
            
        return None
    except Exception as e:
        print(f"[Layer 1] api.list failed: {e}")
        return None

def _parse_transcript_result(transcript_json):
    import json
    if isinstance(transcript_json, str):
        transcript_data = json.loads(transcript_json)
    else:
        transcript_data = transcript_json
    
    # Check if list of dicts or something else
    if isinstance(transcript_data, list):
         return " ".join([t.get('text', '') for t in transcript_data])
    return str(transcript_data)

# --- Layer 2: Translated Captions (Stub) ---
def _get_translated_transcript(video_id):
    # Merged into Layer 1 for simplicity with this library version
    return None

def get_transcript(video_id):
    # 1. Native / Default
    text = _get_native_transcript(video_id)
    if text: return text
    
    # 2. Translated (Placeholder / merged into Layer 1 logic for this lib)
    text = _get_translated_transcript(video_id)
    if text: return text
    
    return "ERROR: No transcript found for this video."

def generate_ai_content(text1, text2):
    if not GEMINI_API_KEY:
        return None

    # Create model with JSON generation config if supported
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 100000, # Attempt to set very high for deep dives
        "response_mime_type": "application/json",
    }
    # Use the specific preview model found in the user's account
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025', generation_config=generation_config)
    
    prompt = f"""
    Analyze these two video transcripts and generate a structured JSON response.
    
    IMPORTANT INSTRUCTIONS FOR "DEEP DIVE" ANALYSIS:
    1. **COMPLETENESS IS CRITICAL**: The user wants every single piece of information. Capture ALL nuances, technical details, and sub-points.
    2. **Language**: If transcripts are in Hindi -> Output strictly in Hindi (Devanagari). If English -> English.
    3. **Long Videos**: Break down content into as many distinct topics as necessary to be exhaustive.
    4. **Coverage**: Do not miss any section.
    
    Transcript 1: {text1[:200000]}... (truncated)
    Transcript 2: {text2[:200000]}... (truncated)

    Output MUST be valid JSON with this exact structure:
    {{
        "summary": [
            {{
                "title": "Comprehensive Topic Name",
                "content": "Detailed, in-depth explanation of this topic. Do not be brief.",
                "subtopics": [
                    {{
                        "heading": "Sub-concept (e.g., Specific Algorithm Step)",
                        "points": ["Detailed technical point 1", "Detailed technical point 2", "Detailed technical point 3", "Examples mentioned"]
                    }}
                ]
            }}
        ],
        "comparativeInsights": {{
            "video1Better": ["Detailed strength 1", "Detailed strength 2"],
            "video2Better": ["Detailed strength 1", "Detailed strength 2"],
            "agreement": ["Detailed point of agreement"]
        }},
        "keyTakeaways": ["Comprehensive takeaway 1", "Comprehensive takeaway 2", "Comprehensive takeaway 3", "Comprehensive takeaway 4"],
        "quiz": [
             {{ "id": 1, "type": "mcq", "question": "Deep technical question...", "options": ["A", "B", "C", "D"], "answer": "A" }}
        ],
        "difficultyQuestions": {{
            "easy": ["Fundamental question 1", "Fundamental question 2"],
            "medium": ["Application-based question 1", "Application-based question 2"],
            "hard": ["Complex analytical question 1", "Complex analytical question 2"]
        }},
        "notes": "Extensive revision notes covering all major concepts..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # In JSON mode, response.text should be clean JSON.
        # But safeguards are good.
        cleaned_text = response.text.replace("```json", "").replace("```", "")
        return json.loads(cleaned_text)
    except Exception as e:
        import traceback
        print(f"ERROR: AI Generation Failed: {e}")
        traceback.print_exc()
        return {"error": str(e)} # Return the error string instead of None to help debug

# Backup Mock Data
MOCK_FALLBACK = {
  "summary": [
    {
      "title": "Fallback Mode",
      "content": "We could not extract subtitles from these videos. Please ensure they have captions allowed."
    }
  ],
  "comparativeInsights": {
      "video1Better": [], "video2Better": [], "agreement": []
  },
  "keyTakeaways": ["Check video privacy settings.", "Ensure videos have CC/Subtitles."],
  "quiz": [],
  "difficultyQuestions": {"easy": [], "medium": [], "hard": []},
  "notes": "Try different videos."
}

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    url1 = data.get('url1')
    url2 = data.get('url2')

    print(f"Processing: {url1} vs {url2}")

    id1 = extract_video_id(url1)
    id2 = extract_video_id(url2)

    if not id1 or not id2:
        return jsonify({"error": "Invalid YouTube URLs"}), 400

    # 1. Fetch Transcripts
    text1 = get_transcript(id1)
    text2 = get_transcript(id2)

    # Check for specific errors
    error_msg = ""
    # "ERROR:" prefix check is a simple way to spy failures from our helpers
    if not text1 or text1.startswith("ERROR:"): 
        error_msg += f"Video 1 ({id1}): {text1} "
    if not text2 or text2.startswith("ERROR:"): 
        error_msg += f"Video 2 ({id2}): {text2} "

    if error_msg:
        print(f"FALLBACK TRIGGERED: {error_msg}")
        fallback_data = MOCK_FALLBACK.copy()
        fallback_data["summary"][0]["content"] = f"TRANSCRIPT FAILURE: {error_msg} (Check terminal for details)"
        return jsonify(fallback_data)

    # 2. Generate AI Content
    ai_result = generate_ai_content(text1, text2)

    if ai_result and "error" not in ai_result:
        return jsonify(ai_result)
    
    # If we got here, AI failed
    error_detail = ai_result.get("error", "Unknown error") if ai_result else "Unknown error"
    print(f"AI FAILURE: {error_detail}")
    
    return jsonify({
        "summary": [{"title": "AI generation failed", "content": f"The AI could not process the request. Error: {error_detail}"}],
        "comparativeInsights": {"video1Better": [], "video2Better": [], "agreement": []},
        "keyTakeaways": [],
        "quiz": [],
        "difficultyQuestions": {"easy": [], "medium": [], "hard": []},
        "notes": "Please check backend logs."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

