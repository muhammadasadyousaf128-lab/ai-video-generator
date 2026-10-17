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


@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


# ---------- HEART-TOUCHING COMPLETE POETRY DATABASE ----------
# Ab random lines nahi mix hongi, balke poori ki poori deep poetry aayegi
POETRY_DATABASE = {
    "sad": [
        "Raat ki tanhai mein teri yaad aati hai,\nDil rota hai magar labon par muskaan aati hai,\nKya karun is zindagi ka jo tere bin adhuri hai,\nHar khushi meri tujhse juda hui zaroori hai,\nTune chhoda toh kya, duniya toh chhod di thi maine,\nTere naam ke siwa kuch nahi bacha is dil mein,\nAb bhi duaon mein tera naam aata hai,\nDard hota hai bohot, par tujhe bhulana nahi aata.",
        
        "Muskurana seekh liya hai humne bhi majboori mein,\nAansu chhupa ke rakh diye hain dil ki aandhi mein,\nLog samajhte hain humein koi gham nahi,\nShayad unhe khabar nahi is toote hue dil ki,\nHar raat takiye ko bhigona aadat ho gayi,\nTeri yaadon mein jalna meri ibadat ho gayi,\nTujhe kho kar bhi tujhe hi dhoondta hoon,\nMain aaj bhi tera hi hoon, bas khud ko bhoolta hoon.",
        
        "Zindagi ne dhoka diya, toh kya hua,\nDil toota, toh kya hua,\nJo chala gaya woh laut kar nahi aata,\nYeh samajhna hi ek bada sabak hai,\nAankhon mein sirf nami reh gayi,\nMeri kahani koi nahi padhta,\nHar muskurahat ke peeche ek dard chhupa hai,\nAkela hoon is bheed mein bhi."
    ],
    "love": [
        "Tere ishq mein humne sab kuch kho diya,\nTujhe chaha toh apne aap ko hi bhula diya,\nTere muskurane par meri duniya basar hoti hai,\nTere ek lafz par meri saari khushi thehar jati hai,\nLog kehte hain ishq ek bimari hai,\nMagar humein toh teri chahat mein guzarna acha lagta hai,\nAgar tu saath hai, toh zindagi jannat hai,\nTere bina yeh dil ek sooni viranat hai.",
        
        "Dil ne tumhe hi chaha tha, phir bhi tum door hue,\nYaadein paas rehti hain, hum majboor hue,\nTumhare liye duniya chhodi, tumne hi chhod diya,\nAansu bhi tumhare naam ke, har lamha jod diya,\nDua mein tumhe maanga tha, Rab ne suna nahi,\nTumhari khushiyan hi meri hain, chahe tum kisi ke ho jao abhi,\nMera pyaar wahi rahega, badlega nahi kabhi,\nTum door hue toh kya hua, dil se gaye nahi kabhi."
    ],
    "motivational": [
        "Jab log tumhein thukrayein toh himmat na haarna,\nKhud par bharosa rakhna aur duniya se na darna,\nGirna toh seekhne ka ek hissa hai,\nHar patthar par thes lagne se insaan nahi banta,\nRaaston mein andhere hain toh khud roshni jalao,\nTumhari manzil tumhara intezaar kar rahi hai,\nBas ek kadam badhao, phir dekho kamaal kya hota hai,\nKabhi na rukna, kyunki jeet tumhara muqaddar hai.",
        
        "Utho, chalo, sapne dekho, har mushkil se aage niklo,\nRaat ke baad subah aati hai, himmat se kaam lo apna,\nMehnat ka phal meetha hota hai, yeh duniya ka usool hai,\nAndhera chahe kitna bhi ho, ek diya tum khud bano,\nRoshni tumse hi aayegi, umeed ka deep jalao,\nMushkil waqt mein bhi hausla na khona tum,\nRab par bharosa rakho, manzil zaroor milegi tumhe,\nApne irado par qaayam raho, kabhi peeche mud ke na dekho."
    ],
    "deep": [
        "Zindagi ek sawaal hai, har jawab khud dhoondhna padta hai,\nJo mila usi mein khush raho, kal ka kisne dekha hai,\nWaqt sabse bara ustaad hai, dard hi asli sabak deta hai,\nKhushiyan pal bhar ki hoti hain, yaadein umar bhar saath rehti hain,\nHar kisi ka apna safar hai, apni apni manzil hai,\nAaj ki mehnat kal ka sona hai, yeh samajh lo,\nTum mein hai bohot dum, bas khud par bharosa rakho,\nSirf ek qadam aur uthao, kamyabi qareeb hai ab."
    ]
}

def generate_local_poetry(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["sad", "toot", "dukh", "breakup", "emotional", "dard"]):
        category = "sad"
    elif any(word in prompt_lower for word in ["love", "ishq", "pyaar", "dil", "romantic"]):
        category = "love"
    elif any(word in prompt_lower for word in ["motivat", "success", "kamyab", "himmat", "mehnat"]):
        category = "motivational"
    else:
        category = "deep"
        
    poetry = random.choice(POETRY_DATABASE[category])
    print(f"✅ Local poetry ({category}):\n{poetry}")
    return poetry

def generate_poetry(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_local_poetry(prompt)

    models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
    
    # GEMINI PROMPT UPDATE: Ab Gemini ko force kiya gaya hai ke woh bohot deep poetry likhe
    instruction = (
        f"You are a deep, heart-touching Urdu poet. Write a VERY emotional poetry in ROMAN URDU (English letters) "
        f"about: {prompt}. Exactly 8 lines. It should be deeply philosophical, sad, or inspiring. "
        f"It must make people cry or feel deeply. No title, no extra text. Just 8 lines separated by newlines."
    )
    payload = {"contents": [{"parts": [{"text": instruction}]}]}

    for model in models:
        for attempt in range(2):
            try:
                url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}")
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

    return generate_local_poetry(prompt)

def generate_voice(poetry_text: str, output_path: str) -> bool:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
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
                voice_settings={"stability": 0.75, "similarity_boost": 0.85, "style": 0.0, "use_speaker_boost": True, "speed": 0.85}
            )
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ Voice ready: {output_path}")
                return True
            else:
                time.sleep(3)
        except Exception as e:
            print(f"⚠️ Voice attempt {attempt+1} fail: {e}")
            time.sleep(5)
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
        for f in os.listdir("."):
            if f.lower().endswith(".mp3") and "test_eleven" not in f:
                music_files.append(f)
    if not music_files:
        return None
    return random.choice(music_files)

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
            params={"query": prompt, "per_page": count, "orientation": "landscape", "size": "large", "page": random_page},
            timeout=30
        )
        if r.status_code == 200:
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
                except:
                    pass
    except Exception as e:
        print(f"❌ Pexels exception: {e}")
    return paths

def fetch_pollinations_images(prompt: str, count: int, folder: str) -> list:
    paths = []
    for i in range(count):
        scene = f"{prompt}, cinematic, 4k"
        encoded = urllib.parse.quote(scene)
        seed = random.randint(1000, 99999)
        url = (f"https://image.pollinations.ai/prompt/{encoded}?width=854&height=480&model=turbo&nologo=true&seed={seed}")
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
                path = os.path.join(folder, f"ai_{i+1}.png")
                with open(path, "wb") as f:
                    f.write(r.content)
                paths.append(path)
            time.sleep(1)
        except:
            pass
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
        
        video_duration = (voice_duration + 1.0) if voice_duration > 0 else 15.0
        video_duration = max(video_duration, 15.0)

        num_images = len(image_paths)
        per_image_duration = video_duration / num_images
        FADE = 0.4

        print(f"🎙️ Voice: {voice_duration:.2f}s, Video: {video_duration:.2f}s")
        
        # 1. Clips generation (480p)
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
                print(f"   ✅ Clip {i+1}/{num_images}")

        if len(clip_files) < 2:
            return False

        # 2. Concat
        concat_list = os.path.join(folder, "concat.txt")
        with open(concat_list, "w") as f:
            for clip in clip_files:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        temp_video1 = os.path.join(folder, "temp1.mp4")
        r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", temp_video1], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return False

        # 3. Overlay
        vf = "scale=854:480,format=yuv420p"
        if poetry_text:
            poetry_filters = build_poetry_drawtext(poetry_text, folder, video_duration)
            if poetry_filters:
                vf = f"scale=854:480,format=yuv420p,{poetry_filters}"

        temp_video2 = os.path.join(folder, "temp2.mp4")
        r = subprocess.run(["ffmpeg", "-y", "-i", temp_video1, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart", temp_video2], capture_output=True, text=True, timeout=180)
        
        if r.returncode != 0:
            shutil.move(temp_video1, temp_video2)
        else:
            print(f"✅ Poetry overlay ready")

        # 4. Audio Mix
        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        if has_voice and music_file:
            cmd_final = [
                "ffmpeg", "-y", "-i", temp_video2, "-i", voice_file, "-i", music_file,
                "-filter_complex", "[1:a]volume=1.5[voice];[2:a]volume=0.25[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
                "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", output_path
            ]
            r = subprocess.run(cmd_final, capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                return True
            else:
                shutil.move(temp_video2, output_path)
                return True
        elif has_voice:
            r = subprocess.run(["ffmpeg", "-y", "-i", temp_video2, "-i", voice_file, "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", output_path], capture_output=True, text=True, timeout=60)
            return True
        elif music_file:
            r = subprocess.run(["ffmpeg", "-y", "-i", temp_video2, "-i", music_file, "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", output_path], capture_output=True, text=True, timeout=60)
            return True
        else:
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

        # Yahan poetry generate ho rahi hai (prompt ke hisaab se)
        poetry = generate_poetry(request.prompt)
        voice_file = os.path.join(folder, "voice.mp3")
        voice_success = generate_voice(poetry, voice_file) if poetry else False

        print("\n🎨 5 images la rahe hain...")
        images = fetch_pexels_images(request.prompt, 5, folder)

        if len(images) < 3:
            needed = 5 - len(images)
            images += fetch_pollinations_images(request.prompt, needed, folder)

        if len(images) < 3:
            return {"status": "error", "message": "Images nahi mili"}

        success = create_video(images, final_path, poetry, voice_file if voice_success else None)

        try:
            shutil.rmtree(folder)
        except:
            pass

        if not success:
            return {"status": "error", "message": "Video creation fail"}

        return {
            "status": "success",
            "video_url": f"/static/{final_filename}",
            "method": "5 Images + Fade + Deep Poetry + Voice + Music",
            "images_used": len(images),
            "poetry": poetry or "",
            "voice": voice_success
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
