from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
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


# ---------- Root route: index.html serve karo ----------
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


# ---------- Emotional Poetry Pool (100+ lines) ----------
POETRY_LINES_POOL = [
    "Aansu chhupa ke hanste hain hum",
    "Dil toota hai phir bhi jee rahe hain",
    "Tanha raaton mein yaad aati hai",
    "Kuch dard aise hote hain",
    "Jo lafzon mein bayan na ho",
    "Khoya hoon apne hi andar",
    "Zindagi ne dhoka diya humein",
    "Phir bhi muskurate hain hum",
    "Rone ki bhi himmat nahi",
    "Aankhon mein sirf nami hai",
    "Jo chala gaya woh laut kar nahi aata",
    "Yaadein sirf yaadein reh jaati hain",
    "Kabhi kabhi khud se darr lagta hai",
    "Akela hoon is bheed mein bhi",
    "Meri kahani koi nahi padhta",
    "Har muskurahat ke peeche ek dard hai",
    "Tumhare bina sab soona hai",
    "Rula ke muskurana seekha hai",
    "Dil ki baat dil mein hi reh gayi",
    "Waqt ne sab kuch badal diya",
    "Zindagi ek sawaal hai",
    "Har jawab khud dhoondhna padta hai",
    "Jo mila usi mein khush raho",
    "Kal ka kisne dekha hai",
    "Aaj ko jee lo poora",
    "Waqt sabse bara ustaad hai",
    "Dard hi asli sabak deta hai",
    "Khushiyan pal bhar ki hoti hain",
    "Yaadein umar bhar saath rehti hain",
    "Har kisi ka apna safar hai",
    "Utho chalo sapne dekho",
    "Har mushkil se aage niklo",
    "Manzil tumhara intezaar kar rahi",
    "Hausla na chhodo kabhi",
    "Raat ke baad subah aati hai",
    "Mehnat ka phal meetha hota hai",
    "Himmat se kaam lo apna",
    "Kamyabi tumhara muqaddar hai",
    "Zindagi ek safar hai",
    "Har din nayi shuruwat hai",
    "Hausla rakho kamiyab hoge",
    "Girna bura nahi hota",
    "Girke na uthna bura hai",
    "Himmat se utho har baar",
    "Jeet tumhari hogi yaar",
    "Andhera chahe kitna bhi ho",
    "Ek diya tum khud bano",
    "Roshni tumse hi aayegi",
    "Umeed ka deep jalao",
    "Mushkil waqt mein bhi",
    "Hausla na khona tum",
    "Rab par bharosa rakho",
    "Manzil zaroor milegi tumhe",
    "Apne irado par qaayam raho",
    "Kabhi peeche mud ke na dekho",
    "Waqt badalta hai har pal",
    "Aaj ki mehnat kal ka sona",
    "Khud par bharosa rakho",
    "Tum mein hai bohot dum",
    "Chalte raho bas chalte raho",
    "Rukna nahi hai tumhe",
    "Kamyabi qareeb hai ab",
    "Sirf ek qadam aur uthao",
    "Hausla buland rakho",
    "Rab ki rehmat se sab hoga",
    "Sabar ka phal meetha hai",
    "Aaj nahi toh kal hoga",
    "Umeed kabhi na chhodo",
    "Apna waqt aayega zaroor",
    "Har subah ek tohfa hai",
    "Tumhari yaad mein jee rahe hain",
    "Dil ne tumhe hi chaha tha",
    "Tum door hue toh kya hua",
    "Yaadein paas rehti hain",
    "Ishq mein sab kho diya humne",
    "Phir bhi pachtate nahi",
    "Tumhare liye duniya chhodi",
    "Tumne hi chhod diya humein",
    "Aansu bhi tumhare naam ke",
    "Dua mein tumhe maanga tha",
    "Rab ne suna nahi humari",
    "Tumhari khushiyan hi meri hain",
    "Chahe tum kisi ke ho jao",
    "Mera pyaar wahi rahega",
    "Nayi subah nayi umeed laati hai",
    "Kal behtar hoga zaroor",
    "Zindagi phir muskura degi",
    "Dard ke baad sukoon aayega",
    "Andhere ke baad roshni hai",
    "Tum akela nahi ho yahan",
    "Hum sab saath hain tumhare",
    "Hausla mat haarna tum",
    "Zindagi tumse pyaar karti hai",
    "Khush raho, muskurao hamesha",
    "Apne aap se pyaar karo",
    "Jo ho gaya use bhool jao",
    "Aage dekho, aage badho",
    "Zindagi bahut khoobsurat hai",
    "Iski qadr karo tum",
]


def generate_local_poetry() -> str:
    lines = random.sample(POETRY_LINES_POOL, 8)
    poetry = "\n".join(lines)
    print(f"✅ Local poetry (random mix):\n{poetry}")
    return poetry


# ---------- Gemini poetry ----------
def generate_poetry(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_local_poetry()

    models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

    instruction = (
        f"Write a DEEP EMOTIONAL motivational poetry in ROMAN URDU (English letters) "
        f"about: {prompt}. "
        f"Exactly 8 lines. No title, no explanation, no quotes, no numbering. "
        f"Just 8 lines of poetry separated by newlines. "
        f"Each line should be short (max 50 characters). "
        f"Make it emotional, touching, and rhyming. "
        f"It should make people feel something deep."
    )

    payload = {"contents": [{"parts": [{"text": instruction}]}]}

    for model in models:
        for attempt in range(2):
            try:
                url = (f"https://generativelanguage.googleapis.com/v1beta/"
                       f"models/{model}:generateContent?key={api_key}")
                print(f"✍️ {model} - attempt {attempt+1}/2...")
                r = requests.post(url, json=payload, timeout=30)

                if r.status_code == 200:
                    data = r.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    poetry = text.strip()
                    lines = [l for l in poetry.split("\n") if l.strip()]
                    if len(lines) >= 4:
                        print(f"✅ Gemini Poetry ready ({len(lines)} lines):\n{poetry}")
                        return poetry
                    else:
                        print(f"⚠️ Gemini ne kam lines di, local use kar rahe hain")
                        break
                elif r.status_code == 503:
                    time.sleep(3)
                elif r.status_code == 404:
                    break
                else:
                    time.sleep(2)
            except Exception as e:
                print(f"   ⚠️ {model} exception: {e}")
                time.sleep(2)

    print("⚠️ Sab Gemini models fail - smart local poetry")
    return generate_local_poetry()


# ---------- ElevenLabs Voice (WITH RETRY) ----------
def generate_voice(poetry_text: str, output_path: str) -> bool:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("⚠️ ELEVENLABS_API_KEY nahi mili")
        return False

    text_for_voice = poetry_text.replace("\n", ". ")

    for attempt in range(3):
        try:
            print(f"🎙️ Voice bana rahe hain (attempt {attempt+1}/3)...")
            client = ElevenLabs(api_key=api_key)

            audio = client.text_to_speech.convert(
                text=text_for_voice,
                voice_id="pNInz6obpgDQGcFmaJgB",
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.75,
                    "similarity_boost": 0.85,
                    "style": 0.0,
                    "use_speaker_boost": True,
                    "speed": 0.85
                }
            )

            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ Voice ready: {output_path}")
                return True
            else:
                print(f"⚠️ Voice file khaali hai, dobara try...")
                time.sleep(3)

        except Exception as e:
            print(f"⚠️ Voice attempt {attempt+1} fail: {e}")
            time.sleep(5)

    print("❌ Voice 3 baar fail - voice ke bina video banayenge")
    return False


# ---------- Audio duration ----------
def get_audio_duration(audio_path: str) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            dur = float(result.stdout.strip())
            print(f"🎙️ Audio duration: {dur:.2f} sec")
            return dur
    except Exception as e:
        print(f"⚠️ FFprobe error: {e}")
    return 0.0


# ---------- Random music ----------
def get_random_music() -> str:
    music_files = []
    if os.path.exists("music"):
        for f in os.listdir("music"):
            if f.lower().endswith((".mp3", ".wav", ".m4a")):
                music_files.append(os.path.join("music", f))
    if not music_files:
        for f in os.listdir("."):
            if f.lower().endswith(".mp3") and "test_eleven" not in f:
                music_files.append(f)
    if not music_files:
        return None
    chosen = random.choice(music_files)
    print(f"🎵 Music chuna: {chosen}")
    return chosen


# ---------- Pexels images ----------
def fetch_pexels_images(prompt: str, count: int, folder: str) -> list:
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return []
    paths = []
    try:
        random_page = random.randint(1, 5)
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": prompt, "per_page": count,
                    "orientation": "landscape", "size": "large",
                    "page": random_page},
            timeout=30
        )
        if r.status_code != 200:
            return []
        photos = r.json().get("photos", [])
        print(f"✅ Pexels: {len(photos)} photos (page {random_page})")
        for i, photo in enumerate(photos):
            url = photo["src"].get("large2x") or photo["src"].get("large")
            try:
                img_r = requests.get(url, timeout=60)
                if img_r.status_code == 200:
                    path = os.path.join(folder, f"pexels_{i+1}.jpg")
                    with open(path, "wb") as f:
                        f.write(img_r.content)
                    paths.append(path)
                    print(f"   ✅ Image {i+1}/{len(photos)}")
            except:
                pass
    except Exception as e:
        print(f"❌ Pexels exception: {e}")
    return paths


def fetch_pollinations_images(prompt: str, count: int, folder: str) -> list:
    paths = []
    for i in range(count):
        scene = f"{prompt}, scene {i+1}, cinematic, 4k"
        encoded = urllib.parse.quote(scene)
        seed = random.randint(1000, 99999)
        url = (f"https://image.pollinations.ai/prompt/{encoded}"
               f"?width=1280&height=720&model=turbo&nologo=true&seed={seed}")
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
                path = os.path.join(folder, f"ai_{i+1}.png")
                with open(path, "wb") as f:
                    f.write(r.content)
                paths.append(path)
            time.sleep(2)
        except:
            pass
    return paths


# ---------- Poetry drawtext (FIXED for Windows + Linux) ----------
def build_poetry_drawtext(poetry_text: str, folder: str, video_duration: float) -> str:
    lines = [l.strip() for l in poetry_text.split("\n") if l.strip()]
    if not lines:
        return ""

    num_lines = len(lines)
    line_duration = video_duration / num_lines

    # Cross-platform font detection
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
            f"drawtext=textfile='{line_path}':"
            f"fontfile='{font_file}':"
            f"fontcolor=white:fontsize=40:"
            f"borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-250:"
            f"enable='between(t\\,{start:.2f}\\,{end:.2f})'"
        )
        filters.append(dt)

    return ",".join(filters)


# ---------- Video with crossfade ----------
def create_video(image_paths, output_path, poetry_text, voice_file):
    try:
        folder = os.path.dirname(image_paths[0])

        voice_duration = 0.0
        if voice_file and os.path.exists(voice_file):
            voice_duration = get_audio_duration(voice_file)

        if voice_duration > 0:
            video_duration = voice_duration + 1.0
        else:
            video_duration = 20.0
        video_duration = max(video_duration, 15.0)

        num_images = len(image_paths)
        CROSSFADE = 0.6
        per_image_duration = (video_duration + (num_images - 1) * CROSSFADE) / num_images

        print(f"🎙️ Voice: {voice_duration:.2f}s, Video: {video_duration:.2f}s")
        print(f"🖼️ {num_images} images, har ek: {per_image_duration:.2f}s, crossfade: {CROSSFADE}s")

        cmd = ["ffmpeg", "-y"]
        for img in image_paths:
            cmd.extend(["-loop", "1", "-t", f"{per_image_duration:.3f}", "-i", img])

        filter_parts = []
        for i in range(num_images):
            filter_parts.append(
                f"[{i}:v]scale=1280:720:force_original_aspect_ratio=decrease,"
                f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p,"
                f"setsar=1,setpts=PTS-STARTPTS[v{i}]"
            )

        current = "[v0]"
        for i in range(1, num_images):
            offset = i * (per_image_duration - CROSSFADE)
            next_label = f"[vx{i}]"
            filter_parts.append(
                f"{current}[v{i}]xfade=transition=fade:"
                f"duration={CROSSFADE}:offset={offset:.3f}{next_label}"
            )
            current = next_label

        if poetry_text:
            poetry_filters = build_poetry_drawtext(poetry_text, folder, video_duration)
            if poetry_filters:
                filter_parts.append(f"{current}{poetry_filters}[vout]")
            else:
                filter_parts.append(f"{current}null[vout]")
        else:
            filter_parts.append(f"{current}null[vout]")

        filter_complex = ";".join(filter_parts)
        temp_video = os.path.join(folder, "final_silent.mp4")

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-t", f"{video_duration:.3f}",
            "-movflags", "+faststart",
            temp_video
        ])

        print(f"🎬 FFmpeg xfade + poetry overlay...")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            print(f"❌ xfade fail: {r.stderr[-500:]}")
            return False

        print(f"✅ Video + transitions + poetry ready")

        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        if has_voice and music_file:
            cmd_final = [
                "ffmpeg", "-y",
                "-i", temp_video,
                "-i", voice_file,
                "-i", music_file,
                "-filter_complex",
                "[1:a]volume=1.5[voice];[2:a]volume=0.25[music];"
                "[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ]
            r = subprocess.run(cmd_final, capture_output=True, text=True, timeout=240)
            if r.returncode == 0:
                print(f"✅ Voice + Music synced")
                return True
            else:
                print(f"⚠️ Voice+Music fail: {r.stderr[-200:]}")
                shutil.move(temp_video, output_path)
                return True
        elif has_voice:
            cmd_final = [
                "ffmpeg", "-y",
                "-i", temp_video,
                "-i", voice_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ]
            r = subprocess.run(cmd_final, capture_output=True, text=True, timeout=180)
            if r.returncode == 0:
                print(f"✅ Voice synced")
                return True
            else:
                shutil.move(temp_video, output_path)
                return True
        elif music_file:
            cmd_final = [
                "ffmpeg", "-y",
                "-i", temp_video,
                "-i", music_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ]
            r = subprocess.run(cmd_final, capture_output=True, text=True, timeout=180)
            if r.returncode == 0:
                print(f"✅ Music added")
                return True
            else:
                shutil.move(temp_video, output_path)
                return True
        else:
            shutil.move(temp_video, output_path)
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------- Main Endpoint ----------
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
        print("=" * 50)

        poetry = generate_poetry(request.prompt)

        voice_file = os.path.join(folder, "voice.mp3")
        voice_success = False
        if poetry:
            voice_success = generate_voice(poetry, voice_file)

        print("\n🎨 10 images la rahe hain...")
        images = fetch_pexels_images(request.prompt, 10, folder)

        if len(images) < 5:
            needed = 10 - len(images)
            print(f"\n⚠️ Pollinations fallback")
            images += fetch_pollinations_images(request.prompt, needed, folder)

        if len(images) < 5:
            return {"status": "error", "message": f"Sirf {len(images)} images mili"}

        print(f"\n✅ Total {len(images)} images ready")
        print("\n🎬 Final video bana rahe hain...")

        success = create_video(
            images, final_path, poetry,
            voice_file if voice_success else None
        )

        try:
            shutil.rmtree(folder)
        except:
            pass

        if not success:
            return {"status": "error", "message": "Video creation fail"}

        size_mb = os.path.getsize(final_path) / 1024 / 1024
        print(f"\n✅ Video ready: {final_filename} ({size_mb:.2f} MB)")
        print("=" * 50 + "\n")

        return {
            "status": "success",
            "video_url": f"/static/{final_filename}",
            "method": "10 Images + Crossfade + Poetry + Voice + Music",
            "images_used": len(images),
            "poetry": poetry or "",
            "voice": voice_success
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
