from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from gtts import gTTS
import uroman as ur
import os
import time
import random
import urllib.parse
import shutil
import subprocess
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

os.makedirs("static", exist_ok=True)
os.makedirs("music", exist_ok=True)

class CORSStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Cache-Control"] = "no-store"
        return response

app.mount("/static", CORSStaticFiles(directory="static"), name="static")

class PromptRequest(BaseModel):
    prompt: str
    background_type: str = "video"
    poetry_type: str = "ai"
    custom_poetry: str = ""

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

POETRY_DATABASE = {
    "sad": [
        "Raat ki tanhai mein teri yaad aati hai,\nDil rota hai magar labon par muskaan aati hai,\nKya karun is zindagi ka jo tere bin adhuri hai,\nHar khushi meri tujhse juda hui zaroori hai.",
        "Muskurana seekh liya hai humne bhi majboori mein,\nAansu chhupa ke rakh diye hain dil ki aandhi mein,\nLog samajhte hain humein koi gham nahi,\nShayad unhe khabar nahi is toote hue dil ki."
    ],
    "love": [
        "Tere ishq mein humne sab kuch kho diya,\nTujhe chaha toh apne aap ko hi bhula diya,\nTere muskurane par meri duniya basar hoti hai,\nTere ek lafz par meri saari khushi thehar jati hai."
    ],
    "motivational": [
        "Jab log tumhein thukrayein toh himmat na haarna,\nKhud par bharosa rakhna aur duniya se na darna,\nGirna toh seekhne ka ek hissa hai,\nHar patthar par thes lagne se insaan nahi banta."
    ],
    "deep": [
        "Zindagi ek sawaal hai, har jawab khud dhoondhna padta hai,\nJo mila usi mein khush raho, kal ka kisne dekha hai,\nWaqt sabse bara ustaad hai, dard hi asli sabak deta hai,\nKhushiyan pal bhar ki hoti hain, yaadein umar bhar saath rehti hain."
    ]
}

def generate_local_poetry(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["sad", "toot", "dukh", "breakup", "emotional"]):
        category = "sad"
    elif any(word in prompt_lower for word in ["love", "ishq", "pyaar", "dil", "romantic"]):
        category = "love"
    elif any(word in prompt_lower for word in ["motivat", "success", "kamyab", "himmat"]):
        category = "motivational"
    else:
        category = "deep"
    return random.choice(POETRY_DATABASE[category])

def convert_to_roman_for_screen(text: str) -> str:
    if any('\u0600' <= char <= '\u06FF' for char in text):
        try:
            uroman_instance = ur.Uroman()
            return uroman_instance.romanize_string(text)
        except: return text
    return text

def convert_roman_to_hindi(text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return text
    
    instruction = (
        f"Convert the following Roman Urdu text into Hindi (Devanagari) script for text-to-speech. "
        f"Output ONLY the Devanagari text.\n\n{text}"
    )
    payload = {"contents": [{"parts": [{"text": instruction}]}]}
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
    
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except: pass
    return text

def generate_poetry(prompt: str, poetry_type: str, custom_poetry: str) -> str:
    if poetry_type == "custom" and custom_poetry.strip():
        return convert_to_roman_for_screen(custom_poetry.strip())
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return generate_local_poetry(prompt)

    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
    instruction = (
        f"You are a legendary, deeply emotional Urdu poet. Write a heart-touching, soulful poetry in ROMAN URDU (English letters) "
        f"about: {prompt}. Exactly 8 lines. Use deep metaphors. "
        f"Do not add any title, explanation, or quotes. Just output the 8 lines separated by newlines."
    )
    payload = {"contents": [{"parts": [{"text": instruction}]}]}

    for model in models:
        try:
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}")
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                data = r.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                lines = [l for l in text.strip().split("\n") if l.strip()]
                if len(lines) >= 4: return "\n".join(lines)
        except: pass
    return generate_local_poetry(prompt)

def generate_voice(screen_poetry: str, original_poetry: str, output_path: str) -> bool:
    try:
        is_urdu_script = any('\u0600' <= char <= '\u06FF' for char in original_poetry)
        
        if is_urdu_script:
            text_for_voice = original_poetry.replace("\n", ". ")
            lang = 'ur'
        else:
            hindi_text = convert_roman_to_hindi(screen_poetry)
            text_for_voice = hindi_text.replace("\n", ". ")
            lang = 'hi'

        tts = gTTS(text=text_for_voice, lang=lang, slow=False)
        tts.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"❌ Voice Error: {e}")
        return False

def get_audio_duration(audio_path: str) -> float:
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return float(result.stdout.strip()) if result.returncode == 0 else 0.0
    except: return 0.0

def get_random_music() -> str:
    music_files = [os.path.join("music", f) for f in os.listdir("music") if f.lower().endswith((".mp3", ".wav"))] if os.path.exists("music") else []
    return random.choice(music_files) if music_files else None

def fetch_pexels_images(prompt: str, count: int, folder: str) -> list:
    api_key = os.getenv("PEXELS_API_KEY")
    paths = []
    try:
        random_page = random.randint(1, 5)
        r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": api_key},
            params={"query": prompt, "per_page": count, "orientation": "portrait", "page": random_page}, timeout=30)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for i, photo in enumerate(photos):
                img_r = requests.get(photo["src"].get("large2x"), timeout=60)
                if img_r.status_code == 200:
                    path = os.path.join(folder, f"img_{i+1}.jpg")
                    with open(path, "wb") as f: f.write(img_r.content)
                    paths.append(path)
    except Exception as e: print(f"❌ Image Error: {e}")
    return paths

def fetch_pexels_videos(prompt: str, count: int, folder: str) -> list:
    api_key = os.getenv("PEXELS_API_KEY")
    paths = []
    try:
        random_page = random.randint(1, 5)
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": api_key},
            params={"query": prompt, "per_page": count, "orientation": "portrait", "page": random_page}, timeout=30)
        if r.status_code == 200:
            videos = r.json().get("videos", [])
            for i, video in enumerate(videos):
                video_files = video.get("video_files", [])
                sd_file = next((v for v in video_files if v["quality"] == "sd"), video_files[0])
                vid_r = requests.get(sd_file.get("link"), timeout=60)
                if vid_r.status_code == 200:
                    path = os.path.join(folder, f"vid_{i+1}.mp4")
                    with open(path, "wb") as f: f.write(vid_r.content)
                    paths.append(path)
    except Exception as e: print(f"❌ Video Error: {e}")
    return paths

def build_poetry_drawtext(poetry_text: str, folder: str, text_duration: float) -> str:
    lines = [l.strip() for l in poetry_text.split("\n") if l.strip()]
    num_lines = len(lines)
    line_duration = text_duration / num_lines
    font_file = "C\\:/Windows/Fonts/arialbd.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    filters = []
    for i, line in enumerate(lines):
        line_file = os.path.join(folder, f"line_{i}.txt")
        with open(line_file, "w", encoding="utf-8") as f: f.write(line)
        line_path = line_file.replace("\\", "/").replace(":", "\\:")
        start, end = i * line_duration, (i + 1) * line_duration
        filters.append(f"drawtext=textfile='{line_path}':fontfile='{font_file}':fontcolor=white:fontsize=30:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-150:enable='between(t\\,{start:.2f}\\,{end:.2f})'")
    return ",".join(filters)

def create_video_from_images(image_paths, output_path, poetry_text, voice_file):
    try:
        folder = os.path.dirname(image_paths[0])
        voice_duration = get_audio_duration(voice_file) if voice_file else 0.0
        
        # 25 Seconds minimum length
        video_duration = max(voice_duration + 2.0, 25.0)
        text_duration = voice_duration if voice_duration > 0 else video_duration
        
        num_images = len(image_paths)
        per_image_duration = video_duration / num_images
        FADE = 0.4

        clip_files = []
        for i, img in enumerate(image_paths):
            clip_path = os.path.join(folder, f"clip_{i}.mp4")
            vf = f"scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p,fade=t=in:st=0:d={FADE},fade=t=out:st={per_image_duration - FADE:.3f}:d={FADE}"
            subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{per_image_duration:.3f}", "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "24", clip_path], capture_output=True, timeout=60)
            clip_files.append(clip_path)

        concat_list = os.path.join(folder, "concat.txt")
        with open(concat_list, "w") as f:
            for clip in clip_files: f.write(f"file '{os.path.abspath(clip)}'\n")

        temp_vid = os.path.join(folder, "temp.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", temp_vid], capture_output=True)

        vf = "scale=720:1280,format=yuv420p"
        if poetry_text: vf = f"scale=720:1280,format=yuv420p,{build_poetry_drawtext(poetry_text, folder, text_duration)}"

        temp_vid_text = os.path.join(folder, "temp_text.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", temp_vid, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", temp_vid_text], capture_output=True)

        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        if has_voice and music_file:
            subprocess.run(["ffmpeg", "-y", "-i", temp_vid_text, "-i", voice_file, "-i", music_file, "-filter_complex", "[1:a]volume=1.5[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=3[aout]", "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{video_duration:.3f}", "-movflags", "+faststart", output_path], capture_output=True)
        elif has_voice:
            subprocess.run(["ffmpeg", "-y", "-i", temp_vid_text, "-i", voice_file, "-c:v", "copy", "-c:a", "aac", "-t", f"{video_duration:.3f}", "-movflags", "+faststart", output_path], capture_output=True)
        else: shutil.move(temp_vid_text, output_path)
        return True
    except Exception as e: print(f"❌ Error Images: {e}"); return False

def create_video_from_clips(video_paths, output_path, poetry_text, voice_file):
    try:
        folder = os.path.dirname(video_paths[0])
        voice_duration = get_audio_duration(voice_file) if voice_file else 0.0
        
        # 25 Seconds minimum length
        video_duration = max(voice_duration + 2.0, 25.0)
        text_duration = voice_duration if voice_duration > 0 else video_duration

        # Yahan hum 5 videos ko loop kar rahe hain taake 25 second pora ho
        concat_file = os.path.join(folder, "clips.txt")
        with open(concat_file, "w") as f:
            for _ in range(5): 
                for vid in video_paths:
                    f.write(f"file '{os.path.abspath(vid)}'\n")

        temp_silent = os.path.join(folder, "temp_silent.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-t", f"{video_duration:.3f}", "-r", "24", temp_silent], capture_output=True, timeout=120)

        vf = "scale=720:1280,format=yuv420p"
        if poetry_text: vf = f"scale=720:1280,format=yuv420p,{build_poetry_drawtext(poetry_text, folder, text_duration)}"

        temp_video_text = os.path.join(folder, "temp_text.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", temp_silent, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", temp_video_text], capture_output=True, timeout=120)

        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        if has_voice and music_file:
            subprocess.run(["ffmpeg", "-y", "-i", temp_video_text, "-i", voice_file, "-i", music_file, "-filter_complex", "[1:a]volume=1.5[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=3[aout]", "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{video_duration:.3f}", "-movflags", "+faststart", output_path], capture_output=True)
        elif has_voice:
            subprocess.run(["ffmpeg", "-y", "-i", temp_video_text, "-i", voice_file, "-c:v", "copy", "-c:a", "aac", "-t", f"{video_duration:.3f}", "-movflags", "+faststart", output_path], capture_output=True)
        else: shutil.move(temp_video_text, output_path)
        return True
    except Exception as e: print(f"❌ Error Videos: {e}"); return False

@app.post("/generate-video")
async def generate_video(request: PromptRequest):
    try:
        ts = int(time.time() * 1000)
        folder = os.path.join("static", f"temp_{ts}")
        os.makedirs(folder, exist_ok=True)
        final_filename = f"output_{ts}.mp4"
        final_path = os.path.join("static", final_filename)

        print(f"\n📝 Prompt: {request.prompt} | Type: {request.background_type} | Poetry: {request.poetry_type}")

        poetry_for_screen = generate_poetry(request.prompt, request.poetry_type, request.custom_poetry)
        
        if not poetry_for_screen:
            return {"status": "error", "message": "Poetry generate nahi ho saki."}

        voice_file = os.path.join(folder, "voice.mp3")
        original_text = request.custom_poetry if request.poetry_type == "custom" else poetry_for_screen
        
        voice_success = generate_voice(poetry_for_screen, original_text, voice_file)

        if request.background_type == "image":
            print("🖼️ Images la rahe hain...")
            images = fetch_pexels_images(request.prompt, 5, folder)
            if len(images) < 2: return {"status": "error", "message": "Images nahi mili"}
            success = create_video_from_images(images, final_path, poetry_for_screen, voice_file if voice_success else None)
        else:
            print("🎬 5 Alag Alag Video Clips la rahe hain...")
            videos = fetch_pexels_videos(request.prompt, 5, folder) # 5 videos mangwayi
            if len(videos) < 1: return {"status": "error", "message": "Videos nahi mili"}
            success = create_video_from_clips(videos, final_path, poetry_for_screen, voice_file if voice_success else None)

        shutil.rmtree(folder, ignore_errors=True)

        if not success: return {"status": "error", "message": "Video fail"}

        return {"status": "success", "video_url": f"/static/{final_filename}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
