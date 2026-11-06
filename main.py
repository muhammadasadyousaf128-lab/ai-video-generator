import os
import time
import random
import shutil
import subprocess
import threading
import requests
import textwrap
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

APP_NAME = "AI Yousaf Studio"
WIDTH = 720
HEIGHT = 1280
FPS = 24 # 24 FPS is standard for Reels and saves RAM
MAX_VIDEO_MB = 15 # Limit each video clip to 15MB
MAX_IMAGE_MB = 8
MAX_DURATION = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
MUSIC_DIR = os.path.join(BASE_DIR, "music")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

app = FastAPI(title=APP_NAME)
GENERATION_LOCK = threading.Lock()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class CORSStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Cache-Control"] = "no-store"
        return response

app.mount("/static", CORSStaticFiles(directory=STATIC_DIR), name="static")

class PromptRequest(BaseModel):
    prompt: str
    background_type: str = "video"
    poetry_type: str = "ai"
    custom_poetry: str = ""
    duration: int = 25
    language: str = "Roman Urdu"
    voice: str = "male"
    music: str = "peaceful"

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
def health():
    return {"status": "online", "app": APP_NAME}

# ==========================================
# AI & VOICE GENERATION
# ==========================================

POETRY_DATABASE = {
    "sad": ["Raat ki tanhai mein teri yaad aati hai,\nKhamosh aankhon se barsaat ho jati hai,\nLog samajhte hain hum khush rehte hain,\nMagar dil mein har roz ek mulaqat hoti hai."],
    "love": ["Tere ishq mein khud ko bhula diya,\nHar khwab tere naam saja diya,\nTu paas ho toh duniya haseen lagti hai,\nTeri muskurahat ne jeena sikha diya."],
    "motivational": ["Gir kar dobara uthna seekh le,\nHar mushkil se ladna seekh le,\nManzil unhi ko milti hai aksar,\nJo haar kar bhi chalna seekh le."],
    "deep": ["Zindagi waqt ka ek safar hai,\nHar chehra apni kahani ka asar hai,\nKuch log mil kar bichhar jaate hain,\nAur kuch yaadon mein amar ho jaate hain."]
}

def generate_local_poetry(prompt):
    p = (prompt or "").lower()
    if any(x in p for x in ["sad", "dukh", "toot", "breakup", "tanhai"]): cat = "sad"
    elif any(x in p for x in ["love", "ishq", "pyaar", "romantic"]): cat = "love"
    elif any(x in p for x in ["motivat", "success", "himmat"]): cat = "motivational"
    else: cat = "deep"
    return random.choice(POETRY_DATABASE[cat])

def gemini_text(instruction, timeout=25):
    key = os.getenv("GEMINI_API_KEY")
    if not key: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": instruction}]}]}, timeout=timeout)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e: print("Gemini error:", e)
    return None

def generate_poetry(prompt, poetry_type, custom_poetry):
    if poetry_type == "custom" and custom_poetry.strip():
        return custom_poetry.strip()
    instruction = f"You are a professional Urdu poet. Write original emotional poetry in Roman Urdu about: {prompt}. Write exactly 4 to 6 short meaningful lines. Output poetry only."
    result = gemini_text(instruction)
    if result:
        lines = [x.strip() for x in result.splitlines() if x.strip()]
        if len(lines) >= 2: return "\n".join(lines[:6])
    return generate_local_poetry(prompt)

def convert_roman_to_hindi(text):
    instruction = f"Convert this Roman Urdu into Devanagari script for Hindi TTS. Preserve Urdu pronunciation. Output converted text only:\n{text}"
    return gemini_text(instruction, 20) or text

def generate_voice(poetry, output_path, language="Roman Urdu"):
    try:
        is_urdu = any("\u0600" <= c <= "\u06FF" for c in poetry)
        if is_urdu:
            voice_text, lang = poetry, "ur"
        elif language.lower() == "english":
            voice_text, lang = poetry, "en"
        else:
            voice_text, lang = convert_roman_to_hindi(poetry), "hi"
        gTTS(text=voice_text.replace("\n", ". "), lang=lang, slow=False).save(output_path)
        return os.path.isfile(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print("Voice error:", e)
        return False

def get_audio_duration(path):
    if not path or not shutil.which("ffprobe"): return 0.0
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True, timeout=15)
        return float(result.stdout.strip()) if result.returncode == 0 else 0.0
    except: return 0.0

# ==========================================
# FFMPEG & PEXELS
# ==========================================

def run_ffmpeg(command, timeout=300):
    if not shutil.which("ffmpeg"): return False
    command = command[:1] + ["-threads", "1", "-filter_threads", "1", "-filter_complex_threads", "1"] + command[1:]
    try:
        with open(os.devnull, "w") as devnull:
            result = subprocess.run(command, stdout=devnull, stderr=subprocess.PIPE, text=True, timeout=timeout)
        if result.returncode:
            print("FFmpeg error:", (result.stderr or "")[-1000:])
            return False
        return True
    except: return False

def get_random_music():
    try:
        files = [os.path.join(MUSIC_DIR, name) for name in os.listdir(MUSIC_DIR) if name.lower().endswith((".mp3", ".wav", ".m4a"))]
        return random.choice(files) if files else None
    except: return None

def download_limited(url, output_path, max_mb, timeout=60):
    limit = max_mb * 1024 * 1024
    total = 0
    try:
        with requests.get(url, stream=True, timeout=(10, timeout)) as response:
            response.raise_for_status()
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    total += len(chunk)
                    if total > limit:
                        file.close(); os.remove(output_path); return False
                    file.write(chunk)
        return os.path.isfile(output_path) and os.path.getsize(output_path) > 1000
    except: 
        if os.path.exists(output_path): os.remove(output_path)
        return False

def fetch_pexels_videos(prompt, folder, count=4):
    key = os.getenv("PEXELS_API_KEY")
    if not key: return []
    try:
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": key}, params={"query": prompt[:100], "per_page": count, "orientation": "portrait"}, timeout=20)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        paths = []
        for i, video in enumerate(videos[:count]):
            for item in video.get("video_files", []):
                link = item.get("link")
                width = int(item.get("width") or 0)
                if link and width <= 720: # Keep small resolution for RAM
                    path = os.path.join(folder, f"vid_{i}.mp4")
                    if download_limited(link, path, MAX_VIDEO_MB):
                        paths.append(path)
                        break
        return paths
    except Exception as e:
        print("Pexels fetch error:", e)
        return []

def fetch_pexels_image(prompt, folder):
    key = os.getenv("PEXELS_API_KEY")
    if not key: return None
    try:
        r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": key}, params={"query": prompt[:100], "per_page": 1, "orientation": "portrait"}, timeout=20)
        if r.status_code == 200 and r.json().get("photos"):
            url = r.json()["photos"][0]["src"]["medium"]
            path = os.path.join(folder, "bg.jpg")
            return path if download_limited(url, path, MAX_IMAGE_MB) else None
    except: pass
    return None

# ==========================================
# VIDEO RENDERING
# ==========================================

def escape_filter_path(path):
    return os.path.abspath(path).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")

def build_subtitle_filter(poetry, folder, duration):
    # Text wrap: Split long lines so they fit on screen
    lines = []
    for line in poetry.splitlines():
        if line.strip():
            wrapped = textwrap.wrap(line.strip(), width=28) # Fit inside 720px width
            lines.extend(wrapped)

    if not lines: return None

    filters = []
    step = duration / len(lines)

    for i, line in enumerate(lines):
        path = os.path.join(folder, f"sub_{i}.txt")
        with open(path, "w", encoding="utf-8") as f: f.write(line)
        
        start, end = i * step, (i + 1) * step
        filters.append(
            f"drawtext=textfile='{escape_filter_path(path)}':"
            f"fontcolor=white:fontsize=38:borderw=3:bordercolor=black:"
            f"shadowcolor=black:shadowx=2:shadowy=2:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:" # Center text perfectly
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )
    return ",".join(filters)

def create_final_video(video_paths, is_image, output, poetry, voice, folder, duration):
    subtitle = build_subtitle_filter(poetry, folder, duration)
    command = ["ffmpeg", "-y"]

    if is_image:
        command += ["-loop", "1", "-framerate", str(FPS), "-i", video_paths[0]]
    else:
        # Create a list to concat all downloaded videos into one long background
        concat_txt = os.path.join(folder, "concat.txt")
        with open(concat_txt, "w") as f:
            for vid in video_paths:
                f.write(f"file '{os.path.abspath(vid)}'\n")
        # Loop the concat file indefinitely
        command += ["-stream_loop", "-1", "-f", "concat", "-safe", "0", "-i", concat_txt]

    has_voice = bool(voice and os.path.isfile(voice))
    music = get_random_music()
    if has_voice: command += ["-i", voice]
    if music: command += ["-stream_loop", "-1", "-i", music]

    # Crop to 9:16 Reels size
    vf = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS},format=yuv420p"
    if subtitle: vf += "," + subtitle

    command += ["-vf", vf, "-map", "0:v:0"]

    if has_voice and music:
        command += ["-filter_complex", "[1:a]volume=1.25[voice];[2:a]volume=0.12[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]", "-map", "[aout]"]
    elif has_voice:
        command += ["-map", "1:a:0"]
    elif music:
        command += ["-map", "1:a:0"]

    command += ["-t", str(duration), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "96k", "-ac", "2", "-movflags", "+faststart", output]

    return run_ffmpeg(command) and os.path.isfile(output) and os.path.getsize(output) > 10000

@app.post("/generate-video")
def generate_video(request: PromptRequest):
    if not GENERATION_LOCK.acquire(blocking=False):
        return {"status": "error", "message": "A video is already generating. Please wait."}
    
    folder = None
    try:
        stamp = int(time.time() * 1000)
        folder = os.path.join(STATIC_DIR, f"temp_{stamp}")
        os.makedirs(folder, exist_ok=True)
        filename = f"output_{stamp}.mp4"
        final_path = os.path.join(STATIC_DIR, filename)

        # 1. Generate Poetry
        poetry = generate_poetry(request.prompt, request.poetry_type, request.custom_poetry)
        if not poetry: return {"status": "error", "message": "Poetry generate fail"}

        # 2. Generate Voice
        voice_path = os.path.join(folder, "voice.mp3")
        voice_ok = generate_voice(poetry, voice_path, request.language)
        if not voice_ok: voice_path = None

        # 3. Calculate Duration
        requested = max(15, min(int(request.duration), MAX_DURATION))
        voice_duration = get_audio_duration(voice_path) if voice_path else 0
        duration = min(MAX_DURATION, max(requested, voice_duration + 2))

        # 4. Fetch Backgrounds
        image_mode = (request.background_type.lower() == "image")
        
        if image_mode:
            bg = fetch_pexels_image(request.prompt, folder)
            video_paths = [bg] if bg else []
        else:
            # Fetch 4 different videos for variety!
            video_paths = fetch_pexels_videos(request.prompt, folder, count=4)
            if not video_paths:
                # Fallback to image if no video found
                bg = fetch_pexels_image(request.prompt, folder)
                if bg:
                    video_paths = [bg]
                    image_mode = True

        if not video_paths:
            return {"status": "error", "message": "Background media not found."}

        # 5. Render
        success = create_final_video(video_paths, image_mode, final_path, poetry, voice_path, folder, duration)

        if not success:
            return {"status": "error", "message": "Video render failed."}

        return {"status": "success", "video_url": f"/static/{filename}", "poetry": poetry, "duration": duration}

    except Exception as e:
        print("MAIN ERROR:", repr(e))
        return {"status": "error", "message": str(e)}
    finally:
        if folder and os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
        GENERATION_LOCK.release()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
