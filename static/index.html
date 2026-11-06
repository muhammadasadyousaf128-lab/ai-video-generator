import os
import time
import random
import shutil
import subprocess
import requests

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from gtts import gTTS

# ==========================================
# 1. BASIC SETTINGS
# ==========================================

load_dotenv()

APP_NAME = "AI Yousaf Studio"

WIDTH = 720
HEIGHT = 1280
FPS = 24

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
MUSIC_DIR = os.path.join(BASE_DIR, "music")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
async def serve_index():
    return FileResponse(
        os.path.join(STATIC_DIR, "index.html")
    )


@app.get("/health")
async def health():
    return {
        "status": "online",
        "app": APP_NAME
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

    prompt = prompt.lower()

    if any(x in prompt for x in [
        "sad", "sadness", "dukh", "toot",
        "breakup", "tanhai", "alone"
    ]):
        category = "sad"

    elif any(x in prompt for x in [
        "love", "ishq", "pyaar", "romantic"
    ]):
        category = "love"

    elif any(x in prompt for x in [
        "motivat", "success", "himmat", "kamyab"
    ]):
        category = "motivational"

    else:
        category = "deep"

    return random.choice(POETRY_DATABASE[category])


# ==========================================
# 5. AI POETRY GENERATION
# ==========================================

def generate_poetry(prompt, poetry_type, custom_poetry):

    if poetry_type == "custom":
        if custom_poetry.strip():
            return custom_poetry.strip()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Gemini key not found. Using local poetry.")
        return generate_local_poetry(prompt)

    instruction = f"""
You are a professional Urdu poet.

Write original, emotional poetry in Roman Urdu.

Topic: {prompt}

Rules:
1. Write exactly 8 lines.
2. Use beautiful Urdu vocabulary.
3. Make the poetry emotional and meaningful.
4. Every line should be suitable for a poetry video.
5. Output only poetry.
6. No title or explanation.
"""

    models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model in models:

        try:

            url = (
                "https://generativelanguage.googleapis.com/"
                f"v1beta/models/{model}:generateContent"
                f"?key={api_key}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": instruction}
                        ]
                    }
                ]
            }

            response = requests.post(
                url,
                json=payload,
                timeout=40
            )

            if response.status_code == 200:

                data = response.json()

                poetry = data["candidates"][0][
                    "content"
                ]["parts"][0]["text"].strip()

                lines = [
                    line.strip()
                    for line in poetry.splitlines()
                    if line.strip()
                ]

                if len(lines) >= 4:
                    return "\n".join(lines[:8])

        except Exception as error:
            print("AI Poetry Error:", error)

    return generate_local_poetry(prompt)


# ==========================================
# 6. ROMAN URDU TO HINDI FOR VOICE
# ==========================================

def convert_roman_to_hindi(text):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return text

    instruction = f"""
Convert this Roman Urdu poetry into Devanagari Hindi script.

Keep the original Urdu pronunciation and meaning.

Output only converted text.

{text}
"""

    models = ["gemini-2.0-flash", "gemini-1.5-flash"]

    for model in models:

        try:

            url = (
                "https://generativelanguage.googleapis.com/"
                f"v1beta/models/{model}:generateContent"
                f"?key={api_key}"
            )

            response = requests.post(
                url,
                json={
                    "contents": [{
                        "parts": [{"text": instruction}]
                    }]
                },
                timeout=30
            )

            if response.status_code == 200:

                result = response.json()

                return result["candidates"][0][
                    "content"
                ]["parts"][0]["text"].strip()

        except Exception as error:
            print("Translation Error:", error)

    return text


# ==========================================
# 7. VOICE GENERATION
# ==========================================

def generate_voice(poetry, output_path, language="Roman Urdu"):

    try:

        is_urdu = any(
            '\u0600' <= char <= '\u06FF'
            for char in poetry
        )

        if is_urdu:
            voice_text = poetry
            voice_language = "ur"

        elif language.lower() in ["english"]:
            voice_text = poetry
            voice_language = "en"

        else:
            voice_text = convert_roman_to_hindi(poetry)
            voice_language = "hi"

        voice_text = voice_text.replace("\n", ". ")

        tts = gTTS(
            text=voice_text,
            lang=voice_language,
            slow=False
        )

        tts.save(output_path)

        return (
            os.path.exists(output_path)
            and os.path.getsize(output_path) > 1000
        )

    except Exception as error:

        print("Voice Error:", error)
        return False


# ==========================================
# 8. AUDIO DURATION
# ==========================================

def get_audio_duration(path):

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
            timeout=30
        )

        if result.returncode == 0:
            return float(result.stdout.strip())

    except Exception as error:
        print("Duration Error:", error)

    return 0.0


# ==========================================
# 9. FFMPEG COMMAND HELPER
# ==========================================

def run_ffmpeg(command, timeout=180):

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            print("FFmpeg Error:", result.stderr[-2000:])
            return False

        return True

    except Exception as error:

        print("FFmpeg Command Error:", error)
        return False


# ==========================================
# 10. RANDOM BACKGROUND MUSIC
# ==========================================

def get_random_music():

    files = [
        os.path.join(MUSIC_DIR, f)
        for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith((".mp3", ".wav"))
    ]

    return random.choice(files) if files else None


# ==========================================
# 11. PEXELS IMAGE DOWNLOAD
# ==========================================

def fetch_pexels_images(prompt, count, folder):

    api_key = os.getenv("PEXELS_API_KEY")

    if not api_key:
        print("PEXELS_API_KEY missing.")
        return []

    paths = []

    try:

        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={
                "query": prompt,
                "per_page": count,
                "orientation": "portrait",
                "page": random.randint(1, 5)
            },
            timeout=30
        )

        response.raise_for_status()

        photos = response.json().get("photos", [])

        for i, photo in enumerate(photos):

            image_url = photo["src"].get("large2x")

            if not image_url:
                continue

            image_response = requests.get(
                image_url,
                timeout=60
            )

            if image_response.status_code == 200:

                path = os.path.join(
                    folder,
                    f"image_{i}.jpg"
                )

                with open(path, "wb") as file:
                    file.write(image_response.content)

                paths.append(path)

    except Exception as error:
        print("Pexels Image Error:", error)

    return paths


# ==========================================
# 12. PEXELS VIDEO DOWNLOAD
# ==========================================

def fetch_pexels_videos(prompt, count, folder):

    api_key = os.getenv("PEXELS_API_KEY")

    if not api_key:
        print("PEXELS_API_KEY missing.")
        return []

    paths = []

    try:

        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={
                "query": prompt,
                "per_page": count,
                "orientation": "portrait",
                "page": random.randint(1, 5)
            },
            timeout=30
        )

        response.raise_for_status()

        videos = response.json().get("videos", [])

        for i, video in enumerate(videos):

            video_files = video.get("video_files", [])

            if not video_files:
                continue

            suitable = sorted(
                video_files,
                key=lambda x: (
                    x.get("width", 0) >= 720,
                    x.get("width", 0)
                ),
                reverse=True
            )

            video_url = suitable[0].get("link")

            if not video_url:
                continue

            video_response = requests.get(
                video_url,
                timeout=120
            )

            if video_response.status_code == 200:

                path = os.path.join(
                    folder,
                    f"video_{i}.mp4"
                )

                with open(path, "wb") as file:
                    file.write(video_response.content)

                paths.append(path)

    except Exception as error:
        print("Pexels Video Error:", error)

    return paths


# ==========================================
# 13. POETRY SUBTITLE FILTER
# ==========================================

def build_poetry_drawtext(poetry, folder, duration):

    lines = [
        line.strip()
        for line in poetry.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    filters = []

    line_duration = duration / len(lines)

    font_file = (
        "C\\:/Windows/Fonts/arialbd.ttf"
        if os.name == "nt"
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )

    for i, line in enumerate(lines):

        text_file = os.path.join(
            folder,
            f"subtitle_{i}.txt"
        )

        with open(text_file, "w", encoding="utf-8") as file:
            file.write(line)

        text_path = text_file.replace("\\", "/")

        if os.name == "nt":
            text_path = text_path.replace(":", "\\:")

        start = i * line_duration
        end = (i + 1) * line_duration

        filters.append(
            "drawtext="
            f"fontfile='{font_file}':"
            f"textfile='{text_path}':"
            "fontcolor=white:"
            "fontsize=32:"
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
# 14. FINAL VIDEO PROCESSING
# ==========================================

def finish_video(
    silent_video,
    output_path,
    poetry,
    voice_file,
    folder,
    duration
):

    subtitle_filter = build_poetry_drawtext(
        poetry,
        folder,
        duration
    )

    subtitled_video = os.path.join(
        folder,
        "subtitled.mp4"
    )

    if subtitle_filter:

        if not run_ffmpeg([
            "ffmpeg", "-y",
            "-i", silent_video,
            "-vf", subtitle_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-an",
            "-movflags", "+faststart",
            subtitled_video
        ]):
            return False

    else:
        subtitled_video = silent_video

    music_file = get_random_music()

    has_voice = (
        voice_file
        and os.path.exists(voice_file)
    )

    if has_voice and music_file:

        command = [
            "ffmpeg", "-y",
            "-i", subtitled_video,
            "-i", voice_file,
            "-stream_loop", "-1",
            "-i", music_file,
            "-filter_complex",
            "[1:a]volume=1.5[voice];"
            "[2:a]volume=0.15[music];"
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration),
            "-movflags", "+faststart",
            output_path
        ]

    elif has_voice:

        command = [
            "ffmpeg", "-y",
            "-i", subtitled_video,
            "-i", voice_file,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-t", str(duration),
            "-movflags", "+faststart",
            output_path
        ]

    elif music_file:

        command = [
            "ffmpeg", "-y",
            "-i", subtitled_video,
            "-stream_loop", "-1",
            "-i", music_file,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-t", str(duration),
            "-movflags", "+faststart",
            output_path
        ]

    else:

        shutil.copy2(subtitled_video, output_path)
        return True

    success = run_ffmpeg(command)

    return (
        success
        and os.path.exists(output_path)
        and os.path.getsize(output_path) > 10000
    )


# ==========================================
# 15. VIDEO FROM IMAGES
# ==========================================

def create_video_from_images(
    images,
    output_path,
    poetry,
    voice_file,
    folder,
    duration
):

    if not images:
        return False

    per_image = duration / len(images)

    clips = []

    for i, image in enumerate(images):

        clip = os.path.join(
            folder,
            f"image_clip_{i}.mp4"
        )

        command = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image,
            "-t", str(per_image),
            "-vf",
            (
                f"scale={WIDTH}:{HEIGHT}:"
                "force_original_aspect_ratio=increase,"
                f"crop={WIDTH}:{HEIGHT},"
                f"fps={FPS},"
                "format=yuv420p,"
                "zoompan=z='min(zoom+0.0005,1.12)':"
                "d=1:s=720x1280:fps=24"
            ),
            "-an",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            clip
        ]

        if not run_ffmpeg(command):
            return False

        clips.append(clip)

    concat_file = os.path.join(
        folder,
        "images_concat.txt"
    )

    with open(concat_file, "w", encoding="utf-8") as file:
        for clip in clips:
            file.write(
                f"file '{os.path.abspath(clip)}'\n"
            )

    silent_video = os.path.join(
        folder,
        "images_silent.mp4"
    )

    if not run_ffmpeg([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        "-t", str(duration),
        silent_video
    ]):
        return False

    return finish_video(
        silent_video,
        output_path,
        poetry,
        voice_file,
        folder,
        duration
    )


# ==========================================
# 16. VIDEO FROM VIDEO CLIPS
# ==========================================

def create_video_from_clips(
    videos,
    output_path,
    poetry,
    voice_file,
    folder,
    duration
):

    if not videos:
        return False

    concat_file = os.path.join(
        folder,
        "videos_concat.txt"
    )

    with open(concat_file, "w", encoding="utf-8") as file:

        # Repeat clips to fill requested duration
        for _ in range(10):
            for video in videos:
                file.write(
                    f"file '{os.path.abspath(video)}'\n"
                )

    silent_video = os.path.join(
        folder,
        "videos_silent.mp4"
    )

    command = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-vf",
        (
            f"scale={WIDTH}:{HEIGHT}:"
            "force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            f"fps={FPS},"
            "format=yuv420p"
        ),
        "-an",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        silent_video
    ]

    if not run_ffmpeg(command, timeout=300):
        return False

    return finish_video(
        silent_video,
        output_path,
        poetry,
        voice_file,
        folder,
        duration
    )


# ==========================================
# 17. MAIN VIDEO GENERATION API
# ==========================================

@app.post("/generate-video")
async def generate_video(request: PromptRequest):

    folder = None

    try:

        timestamp = int(time.time() * 1000)

        folder = os.path.join(
            STATIC_DIR,
            f"temp_{timestamp}"
        )

        os.makedirs(folder, exist_ok=True)

        final_filename = f"output_{timestamp}.mp4"

        final_path = os.path.join(
            STATIC_DIR,
            final_filename
        )

        print("\n================================")
        print("AI YOUSAF STUDIO")
        print("================================")

        print("Prompt:", request.prompt)
        print("Background:", request.background_type)
        print("Poetry Type:", request.poetry_type)

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

        print("Poetry generated successfully.")

        # Generate voice

        voice_file = os.path.join(
            folder,
            "voice.mp3"
        )

        voice_success = generate_voice(
            poetry,
            voice_file,
            request.language
        )

        if voice_success:
            print("Voice generated successfully.")
        else:
            print("Voice unavailable. Continuing without voice.")

        # Calculate video duration

        try:
            requested_duration = max(
                10,
                min(int(request.duration), 120)
            )
        except (ValueError, TypeError):
            requested_duration = 25

        voice_duration = (
            get_audio_duration(voice_file)
            if voice_success else 0
        )

        video_duration = max(
            requested_duration,
            voice_duration + 2
        )

        # Generate background

        if request.background_type.lower() == "image":

            print("Downloading background images...")

            backgrounds = fetch_pexels_images(
                request.prompt,
                5,
                folder
            )

            if not backgrounds:
                return {
                    "status": "error",
                    "message": "Pexels se images nahi milin."
                }

            success = create_video_from_images(
                backgrounds,
                final_path,
                poetry,
                voice_file if voice_success else None,
                folder,
                video_duration
            )

        else:

            print("Downloading background videos...")

            backgrounds = fetch_pexels_videos(
                request.prompt,
                5,
                folder
            )

            if not backgrounds:
                return {
                    "status": "error",
                    "message": "Pexels se videos nahi milin."
                }

            success = create_video_from_clips(
                backgrounds,
                final_path,
                poetry,
                voice_file if voice_success else None,
                folder,
                video_duration
            )

        if not success:
            return {
                "status": "error",
                "message": "Video generation fail ho gayi."
            }

        if not os.path.exists(final_path):
            return {
                "status": "error",
                "message": "Final video file nahi mili."
            }

        video_url = f"/static/{final_filename}"

        print("Video generated successfully!")
        print("Video:", final_path)

        return {
            "status": "success",
            "message": "Video successfully generated!",
            "video_url": video_url,
            "poetry": poetry,
            "duration": video_duration,
            "filename": final_filename
        }

    except Exception as error:

        print("MAIN ERROR:", error)

        return {
            "status": "error",
            "message": str(error)
        }

    finally:

        if folder and os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)


# ==========================================
# 18. RUN SERVER
# ==========================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
