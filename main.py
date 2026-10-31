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
    background_type: str = "video" # Default video

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

# ---------- MASSIVE POETRY DATABASE (100+ Deep Poems) ----------
POETRY_DATABASE = {
    "sad": [
        "Raat ki tanhai mein teri yaad aati hai,\nDil rota hai magar labon par muskaan aati hai,\nKya karun is zindagi ka jo tere bin adhuri hai,\nHar khushi meri tujhse juda hui zaroori hai.",
        "Muskurana seekh liya hai humne bhi majboori mein,\nAansu chhupa ke rakh diye hain dil ki aandhi mein,\nLog samajhte hain humein koi gham nahi,\nShayad unhe khabar nahi is toote hue dil ki.",
        "Ek dard sa seene mein utha hai aaj phir,\nKisi purani yaad ne dil ko chhua hai aaj phir,\nAansu jo sookh gaye thay rukhsaaron par mere,\nKisi ne tera naam liya hai aaj phir.",
        "Tere jaane ke baad yeh dil veeran sa lagta hai,\nHar lamha mujhe ek toofan sa lagta hai,\nLog kehte hain waqt sab bhula deta hai,\nMagar tera chehra toh ab bhi mehmaan sa lagta hai.",
        "Hum toh unhi ke ho gaye jo humare na hue,\nKhud ko bhula baithe unke sahare na hue,\nWoh door gaye toh kya hua, dil mein base hain,\nUnki yaadon ke siwa kuch bhi toh humare na hue.",
        "Dil ki baat labon tak na la sake,\nHum apne hi jazbaat chhupa na sake,\nWoh poochte hain kyun udaas baithe ho,\nKaise batayein ke unhe bhula na sake.",
        "Aankhon mein nami liye baithe hain,\nTeri yaadon ka dard piye baithe hain,\nZamana kehta hai bhool jaao use,\nHum usi ke khyal mein jiye baithe hain.",
        "Jo chala gaya woh laut kar nahi aata,\nPar uski yaad dil se mitati nahi,\nHar mod par bas usi ka intezaar hai,\nZindagi ab aur aage badhti nahi.",
        "Rone ki ijazat nahi, muskurana padta hai,\nDard ko seene mein chhupana padta hai,\nLog poochte hain kya hua hai tumhe,\nBas keh dete hain waqt kharab chal raha hai.",
        "Kisi ki yaad mein raat bhar jagna acha lagta hai,\nUnke khyalon mein khud ko khona acha lagta hai,\nChahe woh humare na ho kabhi,\nPhir bhi unka hi hone ka dawa karna acha lagta hai.",
        "Tere bina zindagi adhuri si lagti hai,\nHar khushi ab mujhe zaroori si lagti hai,\nTune chhoda toh kya, duniya chhod di maine,\nTere naam ke siwa kuch nahi bacha is dil mein.",
        "Ab bhi duaon mein tera naam aata hai,\nDard hota hai bohot, par tujhe bhulana nahi aata.",
        "Har raat takiye ko bhigona aadat ho gayi,\nTeri yaadon mein jalna meri ibadat ho gayi.",
        "Tujhe kho kar bhi tujhe hi dhoondta hoon,\nMain aaj bhi tera hi hoon, bas khud ko bhoolta hoon.",
        "Meri kahani koi nahi padhta,\nMera dard koi nahi samajhta.",
        "Khamoshi meri zubaan ban gayi hai,\nTanhai meri pehchaan ban gayi hai.",
        "Jo dard kabhi bayan nahi hua,\nWoh mere chehre ka nishaan ban gaya hai.",
        "Tumse door hokar bhi tumhari yaad hai,\nDil toh abhi bhi tere hi haath mein hai.",
        "Har muskurahat ke peeche ek dard chhupa hai,\nHar khushi ke peeche ek aansu ruka hai.",
        "Unki galiyon se guzarna aadat ho gayi hai,\nUnka chehra yaad karna ibadat ho gayi hai.",
        "Aankhon mein sirf nami reh gayi,\nMeri khamoshi hi meri zubani reh gayi.",
        "Tere bina jeena seekh liya humne,\nHar dard ko sehna seekh liya humne.",
        "Zindagi ne dhoka diya, toh kya hua,\nDil toota, toh kya hua.",
        "Jo chala gaya woh laut kar nahi aata,\nYeh samajhna hi ek bada sabak hai.",
        "Akela hoon is bheed mein bhi,\nMeri kahani koi nahi padhta."
    ],
    "love": [
        "Tere ishq mein humne sab kuch kho diya,\nTujhe chaha toh apne aap ko hi bhula diya,\nTere muskurane par meri duniya basar hoti hai,\nTere ek lafz par meri saari khushi thehar jati hai.",
        "Dil ne tumhe hi chaha tha, phir bhi tum door hue,\nYaadein paas rehti hain, hum majboor hue,\nTumhare liye duniya chhodi, tumne hi chhod diya,\nAansu bhi tumhare naam ke, har lamha jod diya.",
        "Chahat mein teri humein kya kya nahi mila,\nGham bhi mila, dard bhi mila, ashq bhi mila,\nPhir bhi tere naam par yeh jaan qurbaan hai,\nTeri galiyon mein hi meri pehchaan hai.",
        "Tumhe dekh kar dil ko sukoon milta hai,\nTumse baat karke jahan khilta hai,\nTumhare bina yeh dil udas rehta hai,\nTumse milne ka hi bas intezaar rehta hai.",
        "Pyaar karna tha toh humne kiya,\nTere naam ko apne dil mein liya,\nTune kya kiya yeh toh na poocho,\nHumne toh tujhe har dua mein liya.",
        "Teri baahon mein aakar sukoon milta hai,\nTere ishq mein jeena asaan lagta hai,\nLog kehte hain ishq ek aag hai,\nMagar is aag mein jalna acha lagta hai.",
        "Tumhari yaad mein khoya rehta hoon,\nHar lamha bas tumhe sochta hoon,\nTum door ho magar paas lagte ho,\nDil mein basi ek khoobsurat dard ho.",
        "Tere naam ki khushbu se mehekta hai dil,\nTere ek deedar ko tarasta hai dil,\nKaise batayein tumhe ke kitna pyar hai,\nTere bina jaise bekaar hai dil.",
        "Meri nazar mein tera chehra basa hai,\nMeri saans mein teri khushbu rchi hai,\nMain tera hoon aur rahunga hamesha,\nYeh mohabbat meri tumse sachi hai.",
        "Tere honthon ki muskaan meri duniya hai,\nTeri aankhon ka jadoo meri khushiyan hai,\nTujhe chhune ka khayal aata hai,\nToh jaise khil uthta hai mera aangan.",
        "Meri dhadkan mein tera naam goonjta hai,\nTere bin mera har lamha soona lagta hai.",
        "Tumse milne ki khushi alag hai,\nTumse bichadne ka gham alag hai.",
        "Tum kya jaano is dil ki halat,\nDhadkan pe tere naam ki nishani alag hai.",
        "Tumhari raah mein palkein bichhayi hain,\nTere aane ki umeed par jee rahe hain.",
        "Tujhe dhoondta hoon har mehfil mein,\nTujhe chahta hoon har dhadkan mein.",
        "Tumse shuru, tum par khatam,\nMeri har kahani tumhari hi hai.",
        "Chahu tujhe is qadar, jaise koi deewana apni jaan se pyar kare.",
        "Dil mein armaan hai, aankhon mein khwab hain,\nTumse milne ka hi ek khayal hai.",
        "Tere pyar mein humne din raat kho diye,\nApne saare armaan tere naam kar diye.",
        "Tu hi meri subah, tu hi meri shaam,\nTere naam se hi hain mere saare kaam.",
        "Kabhi sochta hoon tujhe bhool jaun,\nKabhi sochta hoon tujhe kho jaun.",
        "Teri baaton mein ek sukoon hai,\nTera deedar ek khushi ka moosum hai.",
        "Tujhse milne ke baad pata chala,\nIshq kya hota hai aur khushi kya hai.",
        "Tumse milna ek khawab sa lagta hai,\nTumhara hona ek ajeeb sa nasha hai.",
        "Mere dil ki har dhadkan mein tera naam hai,\nMeri har khushi mein tera hi kaam hai."
    ],
    "motivational": [
        "Jab log tumhein thukrayein toh himmat na haarna,\nKhud par bharosa rakhna aur duniya se na darna,\nGirna toh seekhne ka ek hissa hai,\nHar patthar par thes lagne se insaan nahi banta.",
        "Utho, chalo, sapne dekho, har mushkil se aage niklo,\nRaat ke baad subah aati hai, himmat se kaam lo apna,\nMehnat ka phal meetha hota hai, yeh duniya ka usool hai,\nAndhera chahe kitna bhi ho, ek diya tum khud bano.",
        "Zindagi mein kabhi rukna nahi,\nTufaano se kabhi darana nahi,\nJo tu khada hai apne hausle ke dam par,\nToh koi bhi manzil tujhse door nahi.",
        "Haar kar baithna tumhari fitrat nahi,\nMushkil se ghabrana tumhari aadat nahi,\nTum toh woh ho jo toofan se larte hain,\nTumhe rok sakta koi aisi koi taqat nahi.",
        "Manzil milegi zaroor, bas raasta thoda lamba hai,\nHausla rakhna, in raahon mein bas dhalna hai,\nJo log chalte rehte hain apne irado par,\nUnhe rokna kisi ke bas mein nahi hai.",
        "Girna bura nahi hota,\nGirke na uthna bura hai,\nZindagi mein jo sabak milte hain,\nWoh mehnge hote hain, yeh samajhna zaroori hai.",
        "Khud par bharosa rakhna seekho,\nApne sapno par aitmaad rakho,\nLog toh aayenge aur jayenge,\nTum apne irado par qaayam raho.",
        "Mehnat itni karo ke naseeb bhi jhuk jaye,\nKismat tumhare kadmon mein chhalak jaye,\nJab tak sans hai, koshish jaari rakho,\nKabhi toh waqt tumhara bhi badal jaye.",
        "Zindagi ek imtihan hai, pass hona hai,\nHar mushkil ka hal nikalo, yeh karna hai,\nHaar ke aansu ponchh ke phir uthna,\nYehi toh jeena hai, yehi seekhna hai.",
        "Waqt badalta hai, haal badalte hain,\nDin raat ke pahlu badalte hain,\nBas tum apne hausle ko na badalna,\nSabar aur mehnat se manzil milti hai.",
        "Kamyabi ka raasta aasan nahi hota,\nHar kadam par imtihan hota hai.",
        "Jo log haar nahi maante,\nUnka hi har khawab haqeeqat hota hai.",
        "Apne aap ko itna strong banao,\nKe koi bhi tumhe tod na sake.",
        "Tumhare sapno ko koi chura na sake,\nAur tumhe koi rasta mod na sake.",
        "Aag lagao apne andar ki, roshni bano,\nAndhere mein bhi tum apni manzil ko pehchano.",
        "Jo khud par yakeen rakhte hain,\nWoh duniya ki sabse badi taqat hote hain.",
        "Kal ki fikar chhod, aaj par dhyaan de,\nApni kismat ko khud apne haath mein le.",
        "Mehnat karo aisi ke duniya dekhe,\nApne sapno ki tasveer khud apne haath se banaye.",
        "Hausla buland rakho, himmat ko na chhodo,\nMushkil waqt mein bhi apna raasta mat moddo.",
        "Manzil tumhara intezaar kar rahi hai,\nBas thoda aur chalo, phir hasil tumhe hoga.",
        "Tum mein hai woh taqat jo pahaad tod de,\nTum mein hai woh jasba jo duniya ko badal de.",
        "Bas khud par yakeen rakhna seekho,\nKyunki tumse hi toh sab kuch hoga.",
        "Jo log kehte hain tumse nahi hoga,\nUnhe apne kaam se jawab do.",
        "Mehnat se apna muqaddar badlo,\nAur duniya ko tum apna naam dikha do.",
        "Sapne bade dekho, unhe poora karne ki himmat rakho,\nRaaste mushkil hain, magar unse ladhne ki himmat rakho."
    ],
    "deep": [
        "Zindagi ek sawaal hai, har jawab khud dhoondhna padta hai,\nJo mila usi mein khush raho, kal ka kisne dekha hai,\nWaqt sabse bara ustaad hai, dard hi asli sabak deta hai,\nKhushiyan pal bhar ki hoti hain, yaadein umar bhar saath rehti hain.",
        "Kya faida us jeet ka jo dil ko sukoon na de,\nKya faida us safar ka jo manzil tak pahunche hi na,\nLog kehte hain waqt sab bhula deta hai,\nMagar kuch zakhmon ka nishaan hamesha reh jata hai.",
        "Har kisi ka apna safar hai, apni apni manzil hai,\nAaj ki mehnat kal ka sona hai, yeh samajh lo,\nTum mein hai bohot dum, bas khud par bharosa rakho,\nSirf ek qadam aur uthao, kamyabi qareeb hai ab.",
        "Zindagi ek kitab hai, har din ek naya panna,\nKuch khali, kuch likhe hue, kuch adhure se,\nHum padhte hain, samajhte hain, phir bhool jate hain,\nAur ek naya din naye panno ke saath aata hai.",
        "Log kehte hain waqt sab kuch theek kar deta hai,\nMagar waqt toh sirf waqt deta hai,\nTheek hum khud karte hain apne iraado se,\nApne hausle se, apne faislo se.",
        "Duniya ki bheed mein khud ko kho na dena,\nKisi ke kehne par apna rasta chhod na dena,\nTumhari zindagi tumhari hai, khud decide karo,\nKyunki yeh safar sirf tumhe hi tay karna hai.",
        "Rishte aate hain aur chale jate hain,\nKuch yaadein chhod jate hain, kuch zakhm de jate hain,\nMagar jo rishta sachcha ho,\nWoh kabhi dil se nahi jata.",
        "Sach bolna aasan nahi hota,\nSach sunna aur bhi mushkil hota hai,\nMagar jo jhoot ki duniya mein jee raha ho,\nUska sukoon hamesha chin jata hai.",
        "Zindagi mein sab kuch hasil nahi hota,\nKuch cheezein kho kar hi milti hain,\nJo samajh gaya is baat ko,\nWoh zindagi mein kabhi nahi girta.",
        "Kuch log bohot yaad aate hain,\nMagar unka yaad aana unhe wapas nahi laata,\nHum bas unki yaadon mein jee lete hain,\nAur zindagi yun hi guzar jati hai.",
        "Kismat par bharosa mat karo itna,\nKe mehnat karna bhool jao.",
        "Kismat toh unhi ka saath deti hai,\nJo apne haath se apni taqdeer likhte hain.",
        "Muskurana ek ibadat hai,\nKisi ke gham mein kaam aana ek ibadat hai.",
        "Zindagi mein sirf apne liye mat jiyo,\nKisi ke liye jeena bhi ek ibadat hai.",
        "Khushi dhoondne se nahi milti,\nWoh toh andar se paida hoti hai.",
        "Jab tum apne aap se khush hote ho,\nToh duniya ki har cheez khubsurat lagti hai.",
        "Zindagi ek aaina hai,\nJo tum doosron ko dete ho, wohi tumhe milta hai.",
        "Agar pyaar doge toh pyaar milega,\nAgar nafrat doge toh nafrat milegi.",
        "Waqt se pehle aur kismat se zyada,\nKisi ko kuch nahi milta.",
        "Isliye sabar rakho aur mehnat karte raho,\nTumhara waqt zaroor aayega.",
        "Sapne dekhna bura nahi hai,\nMagar unhe poora karne ki koshish karna zaroori hai.",
        "Sirf sapne dekhne wale kabhi kamyab nahi hote,\nKamyab woh hote hain jo unhe poora karte hain.",
        "Duniya mein sabse mushkil kaam hai,\nKhud ko badalna.",
        "Magar jab tum khud ko badal lete ho,\nToh duniya khud badal jati hai.",
        "Log tumhein tab tak nahi samjhenge,\nJab tak tum kamyab nahi ho jate."
    ]
}

def generate_local_poetry(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["sad", "toot", "dukh", "breakup", "emotional", "dard", "rona", "tanha"]):
        category = "sad"
    elif any(word in prompt_lower for word in ["love", "ishq", "pyaar", "dil", "romantic", "chahat"]):
        category = "love"
    elif any(word in prompt_lower for word in ["motivat", "success", "kamyab", "himmat", "mehnat", "jeet"]):
        category = "motivational"
    else:
        category = "deep"
    return random.choice(POETRY_DATABASE[category])

def generate_poetry(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return generate_local_poetry(prompt)

    models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    instruction = (
        f"You are a legendary, deeply emotional Urdu poet. Write a heart-touching, soulful poetry in ROMAN URDU (English letters) "
        f"about: {prompt}. Exactly 8 lines. Use deep metaphors (like stars, darkness, fire, rain). "
        f"It should make the listener feel a deep sense of sadness, love, or motivation. "
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

def generate_voice(poetry_text: str, output_path: str) -> bool:
    text_for_voice = poetry_text.replace("\n", ". ")
    try:
        tts = gTTS(text=text_for_voice, lang='hi', slow=False)
        tts.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except: return False

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
        r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": api_key},
            params={"query": prompt, "per_page": count, "orientation": "portrait"}, timeout=30)
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
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": api_key},
            params={"query": prompt, "per_page": count, "orientation": "portrait"}, timeout=30)
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

def build_poetry_drawtext(poetry_text: str, folder: str, video_duration: float) -> str:
    lines = [l.strip() for l in poetry_text.split("\n") if l.strip()]
    num_lines = len(lines)
    line_duration = video_duration / num_lines
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
        video_duration = (voice_duration + 1.0) if voice_duration > 0 else 15.0
        video_duration = max(video_duration, 15.0)
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
        if poetry_text: vf = f"scale=720:1280,format=yuv420p,{build_poetry_drawtext(poetry_text, folder, video_duration)}"

        temp_vid_text = os.path.join(folder, "temp_text.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", temp_vid, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", temp_vid_text], capture_output=True)

        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        if has_voice and music_file:
            subprocess.run(["ffmpeg", "-y", "-i", temp_vid_text, "-i", voice_file, "-i", music_file, "-filter_complex", "[1:a]volume=1.5[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]", "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", output_path], capture_output=True)
        elif has_voice:
            subprocess.run(["ffmpeg", "-y", "-i", temp_vid_text, "-i", voice_file, "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", output_path], capture_output=True)
        else: shutil.move(temp_vid_text, output_path)
        return True
    except Exception as e: print(f"❌ Error Images: {e}"); return False

def create_video_from_clips(video_paths, output_path, poetry_text, voice_file):
    try:
        folder = os.path.dirname(video_paths[0])
        voice_duration = get_audio_duration(voice_file) if voice_file else 0.0
        video_duration = (voice_duration + 1.0) if voice_duration > 0 else 15.0
        video_duration = max(video_duration, 15.0)

        concat_file = os.path.join(folder, "clips.txt")
        with open(concat_file, "w") as f:
            for vid in video_paths:
                f.write(f"file '{os.path.abspath(vid)}'\n")
                f.write(f"file '{os.path.abspath(vid)}'\n")

        temp_silent = os.path.join(folder, "temp_silent.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-t", f"{video_duration:.3f}", "-r", "24", temp_silent], capture_output=True, timeout=120)

        vf = "scale=720:1280,format=yuv420p"
        if poetry_text: vf = f"scale=720:1280,format=yuv420p,{build_poetry_drawtext(poetry_text, folder, video_duration)}"

        temp_video_text = os.path.join(folder, "temp_text.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", temp_silent, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", temp_video_text], capture_output=True, timeout=120)

        music_file = get_random_music()
        has_voice = voice_file and os.path.exists(voice_file)

        if has_voice and music_file:
            subprocess.run(["ffmpeg", "-y", "-i", temp_video_text, "-i", voice_file, "-i", music_file, "-filter_complex", "[1:a]volume=1.5[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]", "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", output_path], capture_output=True)
        elif has_voice:
            subprocess.run(["ffmpeg", "-y", "-i", temp_video_text, "-i", voice_file, "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", output_path], capture_output=True)
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

        print(f"\n📝 Prompt: {request.prompt} | Type: {request.background_type}")

        poetry = generate_poetry(request.prompt)
        voice_file = os.path.join(folder, "voice.mp3")
        voice_success = generate_voice(poetry, voice_file) if poetry else False

        if request.background_type == "image":
            print("🖼️ Images la rahe hain...")
            images = fetch_pexels_images(request.prompt, 5, folder)
            if len(images) < 2: return {"status": "error", "message": "Images nahi mili"}
            success = create_video_from_images(images, final_path, poetry, voice_file if voice_success else None)
        else:
            print("🎬 Video Clips la rahe hain...")
            videos = fetch_pexels_videos(request.prompt, 3, folder)
            if len(videos) < 1: return {"status": "error", "message": "Videos nahi mili"}
            success = create_video_from_clips(videos, final_path, poetry, voice_file if voice_success else None)

        shutil.rmtree(folder, ignore_errors=True)

        if not success: return {"status": "error", "message": "Video fail"}

        return {"status": "success", "video_url": f"/static/{final_filename}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
