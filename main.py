from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from gtts import gTTS
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

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

# ---------- POETRY DATABASE ----------
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
        
    poetry = random.choice(POETRY_DATABASE[category])
    return poetry

def generate_poetry(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_local_poetry(prompt)

    models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    instruction = (
        f"Write a heart-touching, soulful poetry in ROMAN URDU (English letters) "
        f"about: {prompt}. Exactly 8 lines. Use deep metaphors. "
        f"Do not add any title or quotes. Just output the 8 lines separated by newlines."
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
                if len(lines) >= 4:
                    return "\n".join(lines)
        except:
            pass

    return generate_local_poetry(prompt)

# ---------- GOOGLE TTS (gTTS) VOICE GENERATION ----------
def generate_voice(poetry_text: str, output_path: str) -> bool:
    text_for_voice = poetry_text.replace("\n", ". ")
    try:
        print(f"🎙️ Google TTS Voice bana rahe hain...")
        # Using 'hi' (Hindi) as it reads Roman Urdu perfectly
        tts = gTTS(text=text_for_voice, lang='hi', slow=False)
        tts.save(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"✅ Voice ready: {output_path}")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Voice fail: {e}")
        return False

def get_audio_duration(audio_path: str) -> float:
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return 0.0

def get_random_music() -> str:
    music_files = []
    if os.path.exists("music"):
        for f in os.listdir("music"):
            if f.lower().endswith((".mp3", ".wav", ".m4a")):
                music_files.append(os.path.join("music", f))
    if not music_files:
        return None
    return random.choice(music_files)

def fetch_pexels_images(prompt: str, count: int, folder: str) -> list:
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return []
    paths = []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": prompt, "per_page": count, "orientation": "landscape"},
            timeout=30
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            print(f"✅ Pexels: {len(photos)} photos")
            for i, photo in enumerate(photos):
                url = photo["src"].get("large2x") or photo["src"].get("large")
                try:
                    img_r = requests.get(url, timeout=60)
                    if img_r.status_code == 200:
                        path = os.path.join(folder, f"pexels_{i+1}.jpg")
                        with open(path, "wb") as f:
                            f.write(img_r.content)
                        paths.append(path)
                except:
                    pass
    except Exception as e:
        print(f"❌ Pexels exception: {e}")
    return paths

def build_poetry_drawtext(poetry_text: str, folder: str, video_duration: float) -> str:
    lines = [l.strip() for l in poetry_text.split("\n") if l.strip()]
    if not lines:
        return ""

    num_lines = len(lines)
    line_duration = video_duration / num_lines

    if os.name == 'nt':
        font_file = "C\\:/Windows/Fonts/arialbd.ttf"
    else:
        font_file = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

    filters = []
    for i, line in enumerate(lines):
        line_file = os.path.join(folder, f"line_{i}.txt")
        with open(line_file, "w", encoding="utf-8") as f:
            f.write(line)

        line_path = line_file.replace("\\", "/").replace(":", "\\:")
        start = i * line_duration
        end = (i + 1) * line_duration

        dt = (
            f"drawtext=textfile='{line_path}':fontfile='{font_file}':"
            f"fontcolor=white:fontsize=30:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-150:enable='between(t\\,{start:.2f}\\,{end:.2f})'"
        )
        filters.append(dt)
    return ",".join(filters)

def create_video(image_paths, output_path, poetry_text, voice_file):
    try:
        folder = os.path.dirname(image_paths[0])
        voice_duration = get_audio_duration(voice_file) if (voice_file and os.path.exists(voice_file)) else 0.0
        
        # Video length = voice length + 1 sec (or min 15s)
        video_duration = (voice_duration + 1.0) if voice_duration > 0 else 15.0
        video_duration = max(video_duration, 15.0)

        num_images = len(image_paths)
        per_image_duration = video_duration / num_images
        FADE = 0.4

        print(f"🎙️ Voice: {voice_duration:.2f}s, Video: {video_duration:.2f}s")
        
        clip_files = []
        for i, img in enumerate(image_paths):
            clip_path = os.path.join(folder, f"clip_{i}.mp4")
            vf = (
                f"scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,"
                f"fps=24,format=yuv420p,fade=t=in:st=0:d={FADE},fade=t=out:st={per_image_duration - FADE:.3f}:d={FADE}"
            )
            cmd_clip = [
                "ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{per_image_duration:.3f}",
                "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "24", clip_path
            ]
            r = subprocess.run(cmd_clip, capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                clip_files.append(clip_path)

        if len(clip_files) < 2:
            return False

        concat_list = os.path.join(folder, "concat.txt")
        with open(concat_list, "w") as f:
            for clip in clip_files:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        temp_video1 = os.path.join(folder, "temp1.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", temp_video1], capture_output=True, text=True, timeout=60)

        vf = "scale=854:480,format=yuv420p"
        if poetry_text:
            poetry_filters = build_poetry_drawtext(poetry_text, folder, video_duration)
            if poetry_filters:
                vf = f"scale=854:480,format=yuv420p,{poetry_filters}"

        temp_video2 = os.path.join(folder, "temp2.mp4")
        r = subprocess.run(["ffmpeg", "-y", "-i", temp_video1, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart", temp_video2], capture_output=True, text=True, timeout=180)
        
        if r.returncode != 0:
            shutil.move(temp_video1, temp_video2)

        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        # FINAL MIXING (Robust Command)
        if has_voice and music_file:
            print(f"🎵 Adding Voice + Music...")
            cmd_final = [
                "ffmpeg", "-y",
                "-i", temp_video2,
                "-i", voice_file,
                "-i", music_file,
                "-filter_complex",
                "[1:a]volume=1.5[voice];[2:a]volume=0.2[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=2[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", output_path
            ]
            r = subprocess.run(cmd_final, capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                print(f"✅ Final Video with Voice & Music Ready")
                return True
            else:
                print(f"❌ Mixing failed! Error: {r.stderr[-500:]}")
                shutil.move(temp_video2, output_path)
                return True
        elif has_voice:
            print(f"🎵 Adding Voice only...")
            r = subprocess.run(["ffmpeg", "-y", "-i", temp_video2, "-i", voice_file, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output_path], capture_output=True, text=True, timeout=120)
            return True
        else:
            print(f"⚠️ No voice generated! Saving silent video.")
            shutil.move(temp_video2, output_path)
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@app.post("/generate-video")
async def generate_video(request: PromptRequest):
    try:
        ts = int(time.time() * 1000)
        folder = os.path.join("static", f"temp_{ts}")
        os.makedirs(folder, exist_ok=True)

        final_filename = f"output_{ts}.mp4"
        final_path = os.path.join("static", final_filename)

        print("\n" + "=" * 50)
        print(f"📝 Prompt: {request.prompt}")

        poetry = generate_poetry(request.prompt)
        voice_file = os.path.join(folder, "voice.mp3")
        voice_success = generate_voice(poetry, voice_file) if poetry else False

        print("\n🎨 5 images la rahe hain...")
        images = fetch_pexels_images(request.prompt, 5, folder)

        if len(images) < 3:
            return {"status": "error", "message": "Images nahi mili"}

        success = create_video(images, final_path, poetry, voice_file if voice_success else None)

        try:
            shutil.rmtree(folder)
        except:
            pass

        return {
            "status": "success",
            "video_url": f"/static/{final_filename}",
            "method": "Voice & Music",
            "voice": voice_success
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
