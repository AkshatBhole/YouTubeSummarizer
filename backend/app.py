import sys
import os
import time
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp
import requests
import re


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

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("GEMINI_API_KEY loaded successfully.")
else:
    print("WARNING: GEMINI_API_KEY not set. AI features will be disabled.")



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

# --- Layer 2: yt-dlp Fallback ---
def _parse_json3(data):
    # json3 format: events -> segs -> utf8
    text = []
    for event in data.get('events', []):
        segs = event.get('segs', [])
        if segs:
             line = "".join([s.get('utf8', '') for s in segs])
             text.append(line)
    return " ".join(text)

def _parse_vtt(vtt_text):
    lines = vtt_text.splitlines()
    text = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if '-->' in line: continue
        if line.startswith('WEBVTT'): continue
        if line.startswith('Kind:'): continue
        if line.startswith('Language:'): continue
        # timestamps look like 00:00:00.000
        
        # Simple regex for tags
        clean_line = re.sub(r'<[^>]+>', '', line)
        if clean_line:
            text.append(clean_line)
            
    # Deduplicate adjacent for VTT (rolling captions style)
    deduped = []
    if text:
        deduped.append(text[0])
        for i in range(1, len(text)):
            if text[i] != text[i-1]:
                deduped.append(text[i])
    return " ".join(deduped)

def _get_transcript_ytdlp(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', # Harmless if missing
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[Layer 2] Exploring with yt-dlp for {video_id}...")
            info = ydl.extract_info(url, download=False)
            
            subs = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})
            
            # Helper to find url
            def get_best_url(sub_dict, lang_code):
                if lang_code in sub_dict:
                    # Prefer json3, then vtt, then ttml
                    formats = sub_dict[lang_code]
                    for fmt in formats:
                        if fmt.get('ext') == 'json3': return fmt.get('url'), 'json3'
                    for fmt in formats:
                        if fmt.get('ext') == 'vtt': return fmt.get('url'), 'vtt'
                return None, None

            # 1. Try Manual English
            target_url, fmt_type = get_best_url(subs, 'en')
            # 2. Try Auto English
            if not target_url:
                target_url, fmt_type = get_best_url(auto_subs, 'en')
                
            # 3. Fallback to any 'en' key
            if not target_url:
                all_subs = {**subs, **auto_subs}
                for lang in all_subs:
                    if lang.startswith('en'):
                        target_url, fmt_type = get_best_url(all_subs, lang)
                        if target_url: break

            if target_url:
                print(f"[Layer 2] Fetching subs from URL ({fmt_type})")
                r = requests.get(target_url)
                if r.status_code == 200:
                    if fmt_type == 'json3':
                        return _parse_json3(r.json())
                    elif fmt_type == 'vtt':
                        return _parse_vtt(r.text)
                    else:
                        # Fallback for others? assuming text
                        return r.text
            
            print("[Layer 2] No suitable subtitles found via yt-dlp.")
            return None
            
    except Exception as e:
        print(f"[Layer 2] yt-dlp extraction failed: {e}")
        return None

# --- Layer 3: Translated Stub ---
def _get_translated_transcript(video_id):
    # Merged into Layer 1 for simplicity with this library version
    return None

def get_transcript(video_id):
    # 1. Native / Default
    text = _get_native_transcript(video_id)
    if text: return text
    
    # 2. Fallback to yt-dlp (Robust Method)
    text = _get_transcript_ytdlp(video_id)
    if text: return text
    
    # 3. Translated (Stub)
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
    
    Transcript 1: {text1[:350000]}... (truncated)
    Transcript 2: {text2[:350000]}... (truncated)

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

