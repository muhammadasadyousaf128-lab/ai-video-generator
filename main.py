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

# ---------- 100+ HEART-TOUCHING POETRY DATABASE ----------
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
        "Toota hua dil kisi ko dikhaya nahi jata,\nDard ko lafzon mein samjhaya nahi jata,\nAansu bhi ab sookhne lagte hain,\nJab koi apna hi sath nibhata nahi.",
        "Hum zinda hain magar zindagi nahi hai,\nYeh dil khush hai magar khushi nahi hai,\nTum door ho toh sab kuch adhura hai,\nTumhare bina yeh jahan bhi poora nahi hai.",
        "Dil ke zakham kabhi bharte nahi,\nKuch dard kabhi marte nahi,\nJo log chhod kar jaate hain,\nUnke nishaan kabhi mitate nahi.",
        "Aansu chhupane ki aadat ho gayi hai,\nHar dukh ko seene mein dafan karne ki aadat ho gayi hai,\nLog kehte hain hum bohot khushnaseeb hain,\nNahi pata unhe humein gham sehne ki aadat ho gayi hai.",
        "Teri yaad mein har shaam dhalti hai,\nTere bina zindagi bikhri hui chalti hai,\nKaash tu laut aata is adhure dil mein,\nMagar teri raah toh ab kisi aur ko milti hai.",
        "Humne chaha tha use jaan se zyada,\nMagar usne hi humein chhoda tanha,\nAb kisse batayein is dil ka haal,\nJo ek hi tha, wohi na raha.",
        "Raat bhar jaag kar use dhoondte rahe,\nKhud ko hi apne andar dhoondte rahe,\nWoh toh shayad kisi aur ke ho gaye,\nHum abhi bhi purani yaadon mein kho gaye.",
        "Zindagi ne dhoka diya, toh kya hua,\nDil toota, toh kya hua,\nJo chala gaya woh laut kar nahi aata,\nYeh samajhna hi ek bada sabak hai.",
        "Meri kahani koi nahi padhta,\nMera dard koi nahi samajhta,\nMain hi apne zakhmon ko sehta hoon,\nAur khud hi inhein chhupata hoon.",
        "Khamoshi meri zubaan ban gayi hai,\nTanhai meri pehchaan ban gayi hai,\nJo dard kabhi bayan nahi hua,\nWoh mere chehre ka nishaan ban gaya hai.",
        "Tumse door hokar bhi tumhari yaad hai,\nDil toh abhi bhi tere hi haath mein hai,\nLog kehte hain bhool jao use,\nKaise bhoolun jab woh meri hi zaat mein hai.",
        "Har muskurahat ke peeche ek dard chhupa hai,\nHar khushi ke peeche ek aansu ruka hai,\nLog samajhte hain humein koi gham nahi,\nShayad unhe khabar nahi ke humein jeena kya hai.",
        "Waqt ne sab kuch badal diya,\nRishton ko ek nayi udaan de di,\nMagar hum toh wahi khade hain,\nJaise kisi ne humein bhula diya.",
        "Unki galiyon se guzarna aadat ho gayi hai,\nUnka chehra yaad karna ibadat ho gayi hai,\nWoh toh humein bhool kar aage badh gaye,\nHumari toh unki yaad mein qayamat ho gayi hai.",
        "Aankhon mein sirf nami reh gayi,\nMeri khamoshi hi meri zubani reh gayi,\nJo chala gaya woh wapas na aaya,\nUski yaad hi meri kahani reh gayi.",
        "Tere bina jeena seekh liya humne,\nHar dard ko sehna seekh liya humne,\nTere jaane ke baad yeh pata chala,\nKhud ko sambhalna seekh liya humne."
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
        "Dua mein tera naam maanga tha,\nKhuda se sirf tujhe hi paaya tha,\nTune hi chhod diya raah mein,\nPhir bhi tujhe hi apna banaya tha.",
        "Tere bina yeh dil kehta hai,\nKoi kami si hai har jagah,\nTu saath ho toh manzil aasan lage,\nTere bina safar bada mushkil lage.",
        "Ishq ek aisa samundar hai jismein hum doob gaye,\nTumse mil ke apne gham sab bhool gaye,\nTumhari zulfon ki chhaon mein kho gaye,\nTumhare bin jee nahi sakte yeh keh gaye.",
        "Tumhari baaton ka nasha sa hai,\nTere saath ka har lamha naya sa hai,\nTum paas ho toh zindagi complete hai,\nTere bina sab kuch adhura sa hai.",
        "Maine tujhe chaha bhi, tujhe puja bhi,\nTere ishq mein apne aap ko bhula bhi,\nTune mujhe badle mein dard diya,\nPhir bhi maine tujhe duaon mein rakh diya.",
        "Teri aankhon mein kuch aisa jadoo hai,\nKe dekhne wala bas kho jata hai,\nTere ishq mein hum toh woh hain,\nJo bin piye hi matwala ho jata hai.",
        "Tum se milne ki khushi alag hai,\nTum se bichadne ka gham alag hai,\nTum kya jaano is dil ki halat,\nDhadkan pe tere naam ki nishani alag hai.",
        "Tumhari raah mein palkein bichhayi hain,\nTere aane ki umeed par jee rahe hain,\nTum kabhi aa jao palat kar,\nYeh dil bas teri hi yaad mein khoya hai.",
        "Tujhe dhoondta hoon har mehfil mein,\nTujhe chahta hoon har dhadkan mein,\nTeri kami khatam nahi hoti,\nChahe duniya ho meri aankhon mein.",
        "Tumse shuru, tum par khatam,\nMeri har kahani tumhari hi hai,\nChahu tujhe is qadar,\nJaise koi deewana apni jaan se pyar kare.",
        "Dil mein armaan hai, aankhon mein khwab hain,\nTumse milne ka hi ek khayal hai,\nTum aa jao toh poori ho zindagi,\nTere bina bas yahi mera sawaal hai.",
        "Tere pyar mein humne din raat kho diye,\nApne saare armaan tere naam kar diye,\nTu hi meri subah, tu hi meri shaam,\nTere naam se hi hain mere saare kaam.",
        "Kabhi sochta hoon tujhe bhool jaun,\nKabhi sochta hoon tujhe kho jaun,\nMagar dil kehta hai tu toh meri jaan hai,\nTujhe bhool kar main kahan jaun.",
        "Teri baaton mein ek sukoon hai,\nTera deedar ek khushi ka moosum hai,\nTujhse milne ke baad pata chala,\nIshq kya hota hai aur khushi kya hai.",
        "Tumse milna ek khawab sa lagta hai,\nTumhara hona ek ajeeb sa nasha hai,\nTum ho toh sab kuch acha hai,\nTum na ho toh sab soona sa lagta hai.",
        "Mere dil ki har dhadkan mein tera naam hai,\nMeri har khushi mein tera hi kaam hai,\nTujhe bhulana namumkin hai,\nKyunki tu hi meri subah aur shaam hai."
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
        "Kamyabi ka raasta aasan nahi hota,\nHar kadam par imtihan hota hai,\nJo log haar nahi maante,\nUnka hi har khawab haqeeqat hota hai.",
        "Apne aap ko itna strong banao,\nKe koi bhi tumhe tod na sake,\nTumhare sapno ko koi chura na sake,\nAur tumhe koi rasta mod na sake.",
        "Aag lagao apne andar ki, roshni bano,\nAndhere mein bhi tum apni manzil ko pehchano,\nJo khud par yakeen rakhte hain,\nWoh duniya ki sabse badi taqat hote hain.",
        "Kal ki fikar chhod, aaj par dhyaan de,\nApni kismat ko khud apne haath mein le,\nMehnat karo aisi ke duniya dekhe,\nApne sapno ki tasveer khud apne haath se banaye.",
        "Hausla buland rakho, himmat ko na chhodo,\nMushkil waqt mein bhi apna raasta mat moddo,\nManzil tumhara intezaar kar rahi hai,\nBas thoda aur chalо, phir hasil tumhe hoga.",
        "Tum mein hai woh taqat jo pahaad tod de,\nTum mein hai woh jasba jo duniya ko badal de,\nBas khud par yakeen rakhna seekho,\nKyunki tumse hi toh sab kuch hoga.",
        "Jo log kehte hain tumse nahi hoga,\nUnhe apne kaam se jawab do,\nMehnat se apna muqaddar badlo,\nAur duniya ko tum apna naam dikha do.",
        "Sapne bade dekho, unhe poora karne ki himmat rakho,\nRaaste mushkil hain, magar unse ladhne ki himmat rakho,\nZindagi ek baar milti hai, ise bekaar mat jane do,\nApni mehnat se duniya ko apna diwana banao.",
        "Andhere se mat daro, sitare wahi chamakte hain,\nJo raat ke sabse gehre hisse mein bhi jagmagate hain,\nTum bhi apne waqt ka intezaar karo,\nEk din tumhara bhi suraj nikal kar aayega.",
        "Haar kar bhi haar na maan lena,\nApne irado se kabhi ghabrana nahi,\nJo zakhm milte hain raaste mein,\nWoh tumhari manzil ki nishani hain.",
        "Koshish karne walon ki kabhi haar nahi hoti,\nGirne walon ki kabhi zaat nahi hoti,\nJo lagatar chalte rehte hain,\nUnki manzil kabhi door nahi hoti.",
        "Tumhe koi rasta rok sakta hai, hausla nahi,\nTumhe koi tod sakta hai, irada nahi,\nTumhari manzil tumhara intezaar kar rahi hai,\nBas thoda sa aur chalna hai, intezar nahi.",
        "Apni mehnat par itna yakeen rakho,\nKe naseeb ko majboor karke rakh do,\nDuniya ki koi taqat tumhe rok nahi sakti,\nAgar tum khud par vishwas rakho.",
        "Zindagi mein utaar chadhao aate hain,\nKabhi khushi toh kabhi gham satate hain,\nPar jo log apne hausle se nahi girte,\nWahi zindagi mein sabse aage jaate hain.",
        "Suraj bhi roz ast hota hai,\nPhir naye ujaale ke saath wapas aata hai,\nTum bhi apni haar se seekho,\nAur nayi himmat ke saath aage badho.",
        "Choti choti baaton se himmat na haaro,\nBade sapne dekhne ki aadat ko na badlo,\nDuniya mein sab kuch mumkin hai,\nBas tum apna kirdaar na badlo."
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
        "Kismat par bharosa mat karo itna,\nKe mehnat karna bhool jao,\nKismat toh unhi ka saath deti hai,\nJo apne haath se apni taqdeer likhte hain.",
        "Muskurana ek ibadat hai,\nKisi ke gham mein kaam aana ek ibadat hai,\nZindagi mein sirf apne liye mat jiyo,\nKisi ke liye jeena bhi ek ibadat hai.",
        "Khushi dhoondne se nahi milti,\nWoh toh andar se paida hoti hai,\nJab tum apne aap se khush hote ho,\nToh duniya ki har cheez khubsurat lagti hai.",
        "Zindagi ek aaina hai,\nJo tum doosron ko dete ho, wohi tumhe milta hai,\nAgar pyaar doge toh pyaar milega,\nAgar nafrat doge toh nafrat milegi.",
        "Waqt se pehle aur kismat se zyada,\nKisi ko kuch nahi milta,\nIsliye sabar rakho aur mehnat karte raho,\nTumhara waqt zaroor aayega.",
        "Sapne dekhna bura nahi hai,\nMagar unhe poora karne ki koshish karna zaroori hai,\nSirf sapne dekhne wale kabhi kamyab nahi hote,\nKamyab woh hote hain jo unhe poora karte hain.",
        "Duniya mein sabse mushkil kaam hai,\nKhud ko badalna,\nMagar jab tum khud ko badal lete ho,\nToh duniya khud badal jati hai.",
        "Log tumhein tab tak nahi samjhenge,\nJab tak tum kamyab nahi ho jate,\nIsliye kisi ko samjhane mein waqt mat waste karo,\nBas apne kaam se apni pehchaan banao.",
        "Zindagi mein jo bhi hota hai,\nKisi na kisi wajah se hota hai,\nKabhi khushi ke liye, toh kabhi sabak ke liye,\nHar cheez ko khushi se apna lo.",
        "Rishton mein umar nahi, samajh zaroori hoti hai,\nBaaton mein shabd nahi, dil zaroori hota hai,\nPyaar mein waqt nahi, ehsaas zaroori hota hai,\nAur zindagi mein sirf jeena nahi, jee bhar ke jeena zaroori hai.",
        "Kisi ka dil mat todo,\nKyunki dil tootne ke baad jud nahi pata,\nAur agar jud bhi jaye,\nToh us par ek nishaan reh jata hai.",
        "Zindagi bahut choti hai,\nIsliye har pal ko jee bhar ke jiyo,\nKal ka kya pata,\nIsliye aaj ko apna best din banao.",
        "Jo ho gaya woh ho gaya,\nAb uske baare mein soch kar kya faida,\nAage dekho, aage badho,\nZindagi rukne ka naam nahi leti.",
        "Sach bolne mein himmat chahiye hoti hai,\nAur sach sunne mein aur bhi zyada,\nMagar jo sach se ghabrata hai,\nWoh kabhi kisi ka sacha dost nahi ban sakta.",
        "Zindagi mein kuch pal aise aate hain,\nJo hamesha yaad rehte hain,\nKuch log aise milte hain,\nJo dil mein bas jate hain.",
        "Apne aap ko utna hi important samjho,\nJitna tum doosron ke liye ho,\nKyunki duniya mein sab apne kaam se matlab rakhte hain,\nKoi tumhari kadar nahi karega agar tum khud nahi karo."
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
        
    poetry = random.choice(POETRY_DATABASE[category])
    print(f"✅ Local poetry ({category}):\n{poetry}")
    return poetry

def generate_poetry(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_local_poetry(prompt)

    models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
    
    instruction = (
        f"You are a legendary, deeply emotional Urdu poet. Write a heart-touching, soulful poetry in ROMAN URDU (English letters) "
        f"about: {prompt}. "
        f"Exactly 8 lines. Use deep metaphors (like stars, darkness, fire, rain). "
        f"It should make the listener feel a deep sense of sadness, love, or motivation. "
        f"Do not add any title, explanation, or quotes. Just output the 8 lines separated by newlines."
    )
    payload = {"contents": [{"parts": [{"text": instruction}]}]}

    for model in models:
        for attempt in range(3):
            try:
                url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}")
                print(f"✍️ {model} - attempt {attempt+1}/3...")
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

        concat_list = os.path.join(folder, "concat.txt")
        with open(concat_list, "w") as f:
            for clip in clip_files:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        temp_video1 = os.path.join(folder, "temp1.mp4")
        r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", temp_video1], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return False

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
