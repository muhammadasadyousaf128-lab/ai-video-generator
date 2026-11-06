import os
import time
import random
import shutil
import subprocess
import threading
import requests

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from gtts import gTTS

# ==========================================
# 1. BASIC SETTINGS - 512 MB RAM
# ==========================================

load_dotenv()

APP_NAME = "AI Yousaf Studio"

WIDTH = 720
HEIGHT = 1280
FPS = 20

MAX_VIDEO_MB = 35
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


app.mount(
    "/static",
    CORSStaticFiles(directory=STATIC_DIR),
    name="static"
)


# ==========================================
# 2. REQUEST MODEL
# ==========================================

class PromptRequest(BaseModel):
    prompt: str
    background_type: str = "video"
    poetry_type: str = "ai"
    custom_poetry: str = ""
    duration: int = 25
    language: str = "Roman Urdu"
    voice: str = "male"
    music: str = "peaceful"


# ==========================================
# 3. HOME PAGE
# ==========================================

@app.get("/")
def serve_index():
    return FileResponse(
        os.path.join(STATIC_DIR, "index.html")
    )


@app.get("/health")
def health():
    return {
        "status": "online",
        "app": APP_NAME,
        "memory_mode": "low-memory-512mb"
    }


# ==========================================
# 4. LOCAL POETRY DATABASE
# ==========================================

POETRY_DATABASE = {

    "sad": [
        "Raat ki tanhai mein teri yaad aati hai,\n"
        "Khamosh aankhon se barsaat ho jati hai,\n"
        "Log samajhte hain hum khush rehte hain,\n"
        "Magar dil mein har roz ek mulaqat hoti hai.",

        "Kuch yaadein dil se kabhi jaati nahi,\n"
        "Kuch baatein labon tak aati nahi,\n"
        "Hum muskura kar chhupa lete hain gham,\n"
        "Magar aankhein kabhi jhoot bol paati nahi."
    ],

    "love": [
        "Tere ishq mein khud ko bhula diya,\n"
        "Har khwab tere naam saja diya,\n"
        "Tu paas ho toh duniya haseen lagti hai,\n"
        "Teri muskurahat ne jeena sikha diya."
    ],

    "motivational": [
        "Gir kar dobara uthna seekh le,\n"
        "Har mushkil se ladna seekh le,\n"
        "Manzil unhi ko milti hai aksar,\n"
        "Jo haar kar bhi chalna seekh le."
    ],

    "deep": [
        "Zindagi waqt ka ek safar hai,\n"
        "Har chehra apni kahani ka asar hai,\n"
        "Kuch log mil kar bichhar jaate hain,\n"
        "Aur kuch yaadon mein amar ho jaate hain."
    ]
}


def generate_local_poetry(prompt):

    p = (prompt or "").lower()

    if any(x in p for x in [
        "sad", "sadness", "dukh", "toot",
        "breakup", "tanhai", "alone"
    ]):
        category = "sad"

    elif any(x in p for x in [
        "love", "ishq", "pyaar", "romantic"
    ]):
        category = "love"

    elif any(x in p for x in [
        "motivat", "success", "himmat", "kamyab"
    ]):
        category = "motivational"

    else:
        category = "deep"

    return random.choice(POETRY_DATABASE[category])


# ==========================================
# 5. GEMINI FREE TIER AI
# ==========================================

def gemini_text(instruction, timeout=25):

    key = os.getenv("GEMINI_API_KEY")

    if not key:
        return None

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.0-flash:generateContent"
        f"?key={key}"
    )

    try:

        response = requests.post(
            url,
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": instruction}
                        ]
                    }
                ]
            },
            timeout=timeout
        )

        if response.status_code != 200:
            print(
                "Gemini:",
                response.status_code,
                response.text[:400]
            )
            return None

        return response.json()["candidates"][0][
            "content"
        ]["parts"][0]["text"].strip()

    except Exception as error:

        print("Gemini error:", error)
        return None


def generate_poetry(prompt, poetry_type, custom_poetry):

    if poetry_type == "custom" and custom_poetry.strip():
        return custom_poetry.strip()

    instruction = f"""
You are a professional Urdu poet.

Write original emotional poetry in Roman Urdu.

Topic: {prompt}

Write 4 to 8 short meaningful lines.

Output poetry only.
No title or explanation.
"""

    result = gemini_text(instruction)

    if result:

        lines = [
            x.strip()
            for x in result.splitlines()
            if x.strip()
        ]

        if len(lines) >= 2:
            return "\n".join(lines[:8])

    print("Using offline local poetry.")

    return generate_local_poetry(prompt)


# ==========================================
# 6. ROMAN URDU CONVERSION
# ==========================================

def convert_roman_to_hindi(text):

    instruction = (
        "Convert this Roman Urdu into Devanagari "
        "script for Hindi TTS. Preserve Urdu "
        "pronunciation and meaning. Output converted "
        "text only:\n" + text
    )

    return gemini_text(instruction, 20) or text


# ==========================================
# 7. VOICE GENERATION
# ==========================================

def generate_voice(poetry, output_path, language="Roman Urdu"):

    try:

        is_urdu = any(
            "\u0600" <= c <= "\u06FF"
            for c in poetry
        )

        if is_urdu:

            voice_text = poetry
            lang = "ur"

        elif language.lower() == "english":

            voice_text = poetry
            lang = "en"

        else:

            voice_text = convert_roman_to_hindi(poetry)
            lang = "hi"

        gTTS(
            text=voice_text.replace("\n", ". "),
            lang=lang,
            slow=False
        ).save(output_path)

        return (
            os.path.isfile(output_path)
            and os.path.getsize(output_path) > 1000
        )

    except Exception as error:

        print("Voice error:", error)
        return False


# ==========================================
# 8. AUDIO DURATION
# ==========================================

def get_audio_duration(path):

    if not path or not shutil.which("ffprobe"):
        return 0.0

    try:

        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        return (
            float(result.stdout.strip())
            if result.returncode == 0 else 0.0
        )

    except Exception as error:

        print("Audio duration error:", error)
        return 0.0


# ==========================================
# 9. FFMPEG LOW RAM
# ==========================================

def run_ffmpeg(command, timeout=300):

    if not shutil.which("ffmpeg"):
        print("FFmpeg executable not found.")
        return False

    command = command[:1] + [
        "-threads", "1",
        "-filter_threads", "1",
        "-filter_complex_threads", "1"
    ] + command[1:]

    try:

        with open(os.devnull, "w") as devnull:

            result = subprocess.run(
                command,
                stdout=devnull,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )

        if result.returncode:

            print(
                "FFmpeg error:",
                (result.stderr or "")[-2200:]
            )

            return False

        return True

    except subprocess.TimeoutExpired:

        print("FFmpeg timed out.")
        return False

    except Exception as error:

        print("FFmpeg error:", error)
        return False


# ==========================================
# 10. BACKGROUND MUSIC
# ==========================================

def get_random_music():

    try:

        files = [
            os.path.join(MUSIC_DIR, name)
            for name in os.listdir(MUSIC_DIR)
            if name.lower().endswith(
                (".mp3", ".wav", ".m4a")
            )
        ]

        return random.choice(files) if files else None

    except Exception:

        return None


# ==========================================
# 11. LIMITED DOWNLOAD
# ==========================================

def download_limited(
    url,
    output_path,
    max_mb,
    timeout=90
):

    limit = max_mb * 1024 * 1024
    total = 0

    try:

        with requests.get(
            url,
            stream=True,
            timeout=(15, timeout)
        ) as response:

            response.raise_for_status()

            size = response.headers.get("Content-Length")

            if size and int(size) > limit:

                print("Download skipped: over size limit.")
                return False

            with open(output_path, "wb") as file:

                for chunk in response.iter_content(
                    chunk_size=64 * 1024
                ):

                    if not chunk:
                        continue

                    total += len(chunk)

                    if total > limit:

                        file.close()
                        os.remove(output_path)

                        print("Download stopped at size limit.")
                        return False

                    file.write(chunk)

        return (
            os.path.isfile(output_path)
            and os.path.getsize(output_path) > 1000
        )

    except Exception as error:

        print("Download error:", error)

        if os.path.exists(output_path):
            os.remove(output_path)

        return False


# ==========================================
# 12. PEXELS SEARCH
# ==========================================

def pexels_search(endpoint, prompt, key):

    response = requests.get(
        endpoint,
        headers={"Authorization": key},
        params={
            "query": (prompt or "cinematic nature")[:100],
            "per_page": 5,
            "orientation": "portrait",
            "page": 1
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# 13. PEXELS VIDEO
# ==========================================

def fetch_one_pexels_video(prompt, folder):

    key = os.getenv("PEXELS_API_KEY")

    if not key:
        print("PEXELS_API_KEY missing.")
        return None

    try:

        data = pexels_search(
            "https://api.pexels.com/videos/search",
            prompt,
            key
        )

        choices = []

        for video in data.get("videos", []):

            for item in video.get("video_files", []):

                link = item.get("link")

                width = int(item.get("width") or 0)
                height = int(item.get("height") or 0)

                if link and width >= 240 and height >= width:
                    choices.append((width, link))

        choices.sort(
            key=lambda x: abs(x[0] - 480)
        )

        for i, (_, link) in enumerate(choices[:3]):

            path = os.path.join(
                folder,
                f"background_{i}.mp4"
            )

            if download_limited(
                link,
                path,
                MAX_VIDEO_MB
            ):
                return path

    except Exception as error:

        print("Pexels video error:", error)

    return None


# ==========================================
# 14. PEXELS IMAGE FALLBACK
# ==========================================

def fetch_one_pexels_image(prompt, folder):

    key = os.getenv("PEXELS_API_KEY")

    if not key:
        print("PEXELS_API_KEY missing.")
        return None

    try:

        data = pexels_search(
            "https://api.pexels.com/v1/search",
            prompt,
            key
        )

        photos = data.get("photos", [])

        if not photos:
            return None

        url = random.choice(photos).get(
            "src", {}
        ).get("medium")

        if not url:
            return None

        path = os.path.join(
            folder,
            "background.jpg"
        )

        return (
            path
            if download_limited(
                url,
                path,
                MAX_IMAGE_MB,
                60
            )
            else None
        )

    except Exception as error:

        print("Pexels image error:", error)
        return None


# ==========================================
# 15. SUBTITLES
# ==========================================

def escape_filter_path(path):

    value = os.path.abspath(path).replace("\\", "/")

    return value.replace(":", r"\:").replace("'", r"\'")


def build_subtitle_filter(poetry, folder, duration):

    lines = [
        x.strip()
        for x in poetry.splitlines()
        if x.strip()
    ][:8]

    if not lines:
        return None

    filters = []
    step = duration / len(lines)

    for i, line in enumerate(lines):

        path = os.path.join(
            folder,
            f"subtitle_{i}.txt"
        )

        with open(path, "w", encoding="utf-8") as file:
            file.write(line)

        start = i * step
        end = (i + 1) * step

        filters.append(
            "drawtext=textfile='"
            + escape_filter_path(path)
            + "':"
            "fontcolor=white:"
            "fontsize=34:"
            "borderw=3:"
            "bordercolor=black:"
            "shadowcolor=black:"
            "shadowx=2:"
            "shadowy=2:"
            "x=(w-text_w)/2:"
            "y=h-220:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )

    return ",".join(filters)


# ==========================================
# 16. FINAL VIDEO RENDER
# ==========================================

def create_final_video(
    background,
    is_image,
    output,
    poetry,
    voice,
    folder,
    duration
):

    subtitle = build_subtitle_filter(
        poetry,
        folder,
        duration
    )

    command = ["ffmpeg", "-y"]

    if is_image:

        command += [
            "-loop", "1",
            "-framerate", str(FPS),
            "-i", background
        ]

    else:

        command += [
            "-stream_loop", "-1",
            "-i", background
        ]

    has_voice = bool(
        voice and os.path.isfile(voice)
    )

    music = get_random_music()

    if has_voice:
        command += ["-i", voice]

    if music:
        command += [
            "-stream_loop", "-1",
            "-i", music
        ]

    vf = (
        f"scale={WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"fps={FPS},"
        "format=yuv420p"
    )

    if subtitle:
        vf += "," + subtitle

    command += [
        "-vf", vf,
        "-map", "0:v:0"
    ]

    if has_voice and music:

        command += [
            "-filter_complex",
            "[1:a]volume=1.25[voice];"
            "[2:a]volume=0.12[music];"
            "[voice][music]amix=inputs=2:"
            "duration=first:dropout_transition=2[aout]",
            "-map", "[aout]"
        ]

    elif has_voice:

        command += ["-map", "1:a:0"]

    elif music:

        command += ["-map", "1:a:0"]

    command += [
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "96k",
        "-ac", "2",
        "-movflags", "+faststart",
        "-threads", "1",
        output
    ]

    success = run_ffmpeg(command)

    return (
        success
        and os.path.isfile(output)
        and os.path.getsize(output) > 10000
    )


# ==========================================
# 17. MAIN VIDEO GENERATION API
# ==========================================

@app.post("/generate-video")
def generate_video(request: PromptRequest):

    if not GENERATION_LOCK.acquire(blocking=False):

        return {
            "status": "error",
            "message": "A video is already being generated. Please wait."
        }

    folder = None

    try:

        if not shutil.which("ffmpeg"):

            return {
                "status": "error",
                "message": "FFmpeg server par installed nahi hai."
            }

        stamp = int(time.time() * 1000)

        folder = os.path.join(
            STATIC_DIR,
            f"temp_{stamp}"
        )

        os.makedirs(folder, exist_ok=True)

        filename = f"output_{stamp}.mp4"

        final_path = os.path.join(
            STATIC_DIR,
            filename
        )

        print("AI YOUSAF STUDIO - LOW RAM MODE")
        print("Prompt:", request.prompt)
        print("Background:", request.background_type)

        # Generate poetry

        poetry = generate_poetry(
            request.prompt,
            request.poetry_type,
            request.custom_poetry
        )

        if not poetry:

            return {
                "status": "error",
                "message": "Poetry generate nahi ho saki."
            }

        # Generate voice

        voice_path = os.path.join(
            folder,
            "voice.mp3"
        )

        voice_ok = generate_voice(
            poetry,
            voice_path,
            request.language
        )

        if not voice_ok:
            voice_path = None

        # Duration

        try:

            requested = max(
                10,
                min(int(request.duration), MAX_DURATION)
            )

        except (ValueError, TypeError):

            requested = 25

        voice_duration = (
            get_audio_duration(voice_path)
            if voice_path else 0
        )

        duration = min(
            MAX_DURATION,
            max(requested, voice_duration + 2)
        )

        # Background

        image_mode = (
            request.background_type.lower() == "image"
        )

        if image_mode:

            print("Fetching one Pexels image...")

            background = fetch_one_pexels_image(
                request.prompt,
                folder
            )

        else:

            print("Fetching one small Pexels video...")

            background = fetch_one_pexels_video(
                request.prompt,
                folder
            )

        # Automatic image fallback

        if not background and not image_mode:

            print("Video unavailable; trying image fallback.")

            background = fetch_one_pexels_image(
                request.prompt,
                folder
            )

            image_mode = True

        if not background:

            return {
                "status": "error",
                "message": "Pexels background nahi mila. API key aur prompt check karein."
            }

        # Render video

        print("Rendering video with low-memory FFmpeg settings...")

        success = create_final_video(
            background,
            image_mode,
            final_path,
            poetry,
            voice_path,
            folder,
            duration
        )

        if not success:

            return {
                "status": "error",
                "message": "Video render fail hui. Render logs mein FFmpeg error check karein."
            }

        return {
            "status": "success",
            "message": "Video successfully generated!",
            "video_url": f"/static/{filename}",
            "poetry": poetry,
            "duration": duration,
            "filename": filename
        }

    except Exception as error:

        print("MAIN ERROR:", repr(error))

        return {
            "status": "error",
            "message": str(error)
        }

    finally:

        if folder and os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)

        GENERATION_LOCK.release()


# ==========================================
# 18. RUN SERVER
# ==========================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000"))
    )
