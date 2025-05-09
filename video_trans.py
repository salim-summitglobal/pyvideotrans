import os
import requests
import re
import time
from pathlib import Path

# Import videotrans modules
from videotrans.configure import config

# Configuration
VIDEO_DIR = "/home/sgt/Downloads/test"
ROOT_DIR = config.ROOT_DIR
HOST = "127.0.0.1"
PORT = 9011
API_URL = f"http://{HOST}:{PORT}/trans_video"
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv')

# Read host configuration if available
if Path(ROOT_DIR+'/host.txt').is_file():
    host_str = Path(ROOT_DIR+'/host.txt').read_text(encoding='utf-8').strip()
    host_str = re.sub(r'https?://','', host_str).split(':')
    if len(host_str) > 0:
        HOST = host_str[0]
    if len(host_str) == 2:
        PORT = int(host_str[1])
        API_URL = f"http://{HOST}:{PORT}/trans_video"

def find_video_files(directory: str) -> list[str]:
    """Find all video files in the specified directory."""
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Folder not found: {directory}")

    videos = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.lower().endswith(VIDEO_EXTENSIONS)
    ]

    return videos



def process_video(filepath: str) -> None:
    try:
        data = {
            "name": filepath,
            "recogn_type": 0,
            "split_type": "overall",
            "model_name": "tiny",
            "detect_language": "auto",
            "translate_type": 0,
            "source_language": "auto",
            "target_language": "en",
            "tts_type": 0,
            "voice_role": "zh-CN-YunjianNeural",
            "voice_rate": "+0%",
            "volume": "+0%",
            "pitch": "+0Hz",
            "voice_autorate": True,
            "video_autorate": True,
            "is_separate": False,
            "back_audio": "",
            "subtitle_type": 1,
            "append_video": False,
            "is_cuda": False,
        }

        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 0:
            task_id = result.get('task_id', 'unknown')
            print(f"✓ Success: {os.path.basename(filepath)} → Task ID: {task_id}")
            return task_id
        else:
            error_msg = result.get('msg', 'Unknown error')
            print(f"✗ Error: {os.path.basename(filepath)} → {error_msg}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed: {os.path.basename(filepath)} → {e}")
        return None

if __name__ == "__main__":
    video_files = find_video_files(VIDEO_DIR)
    total_videos = len(video_files)

    if total_videos == 0:
        print(f"No videos found in {VIDEO_DIR}")
        exit(0)

    print(f"Found {total_videos} video(s) to process:")
    for video in video_files:
        print(f"  • {os.path.basename(video)}")

    print("\nStarting audio detection and processing...")

    successful = 0
    task_ids = []

    for idx, video in enumerate(video_files):
        print(f"\nProcessing video {idx+1}/{total_videos}...")
        task_id = process_video(video)

        if task_id:
            successful += 1
            task_ids.append(task_id)

        if idx < total_videos - 1:
            time.sleep(1)

    print(f"\nProcessing complete: {successful}/{total_videos} videos successfully submitted")

    if task_ids:
        print("\nTask IDs:")
        for task_id in task_ids:
            print(f"  • {task_id}")







# {
#     "ar": [
#         "No",
#         "ar-DZ-AminaNeural",
#         "ar-DZ-IsmaelNeural",
#         "ar-BH-AliNeural",
#         "ar-BH-LailaNeural",
#         "ar-EG-SalmaNeural",
#         "ar-EG-ShakirNeural",
#         "ar-IQ-BasselNeural",
#         "ar-IQ-RanaNeural",
#         "ar-JO-SanaNeural",
#         "ar-JO-TaimNeural",
#         "ar-KW-FahedNeural",
#         "ar-KW-NouraNeural",
#         "ar-LB-LaylaNeural",
#         "ar-LB-RamiNeural",
#         "ar-LY-ImanNeural",
#         "ar-LY-OmarNeural",
#         "ar-MA-JamalNeural",
#         "ar-MA-MounaNeural",
#         "ar-OM-AbdullahNeural",
#         "ar-OM-AyshaNeural",
#         "ar-QA-AmalNeural",
#         "ar-QA-MoazNeural",
#         "ar-SA-HamedNeural",
#         "ar-SA-ZariyahNeural",
#         "ar-SY-AmanyNeural",
#         "ar-SY-LaithNeural",
#         "ar-TN-HediNeural",
#         "ar-TN-ReemNeural",
#         "ar-AE-FatimaNeural",
#         "ar-AE-HamdanNeural",
#         "ar-YE-MaryamNeural",
#         "ar-YE-SalehNeural"
#     ],
#     "zh": [
#         "No",
#         "zh-HK-HiuGaaiNeural",
#         "zh-HK-HiuMaanNeural",
#         "zh-HK-WanLungNeural",
#         "zh-CN-XiaoxiaoNeural",
#         "zh-CN-XiaoyiNeural",
#         "zh-CN-YunjianNeural",
#         "zh-CN-YunxiNeural",
#         "zh-CN-YunxiaNeural",
#         "zh-CN-YunyangNeural",
#         "zh-CN-liaoning-XiaobeiNeural",
#         "zh-TW-HsiaoChenNeural",
#         "zh-TW-YunJheNeural",
#         "zh-TW-HsiaoYuNeural",
#         "zh-CN-shaanxi-XiaoniNeural"
#     ],
#     "cs": [
#         "No",
#         "cs-CZ-AntoninNeural",
#         "cs-CZ-VlastaNeural"
#     ],
#     "nl": [
#         "No",
#         "nl-BE-ArnaudNeural",
#         "nl-BE-DenaNeural",
#         "nl-NL-ColetteNeural",
#         "nl-NL-FennaNeural",
#         "nl-NL-MaartenNeural"
#     ],
#     "en": [
#         "No",
#         "en-AU-NatashaNeural",
#         "en-AU-WilliamNeural",
#         "en-CA-ClaraNeural",
#         "en-CA-LiamNeural",
#         "en-HK-SamNeural",
#         "en-HK-YanNeural",
#         "en-IN-NeerjaExpressiveNeural",
#         "en-IN-NeerjaNeural",
#         "en-IN-PrabhatNeural",
#         "en-IE-ConnorNeural",
#         "en-IE-EmilyNeural",
#         "en-KE-AsiliaNeural",
#         "en-KE-ChilembaNeural",
#         "en-NZ-MitchellNeural",
#         "en-NZ-MollyNeural",
#         "en-NG-AbeoNeural",
#         "en-NG-EzinneNeural",
#         "en-PH-JamesNeural",
#         "en-US-AvaNeural",
#         "en-US-AndrewNeural",
#         "en-US-EmmaNeural",
#         "en-US-BrianNeural",
#         "en-PH-RosaNeural",
#         "en-SG-LunaNeural",
#         "en-SG-WayneNeural",
#         "en-ZA-LeahNeural",
#         "en-ZA-LukeNeural",
#         "en-TZ-ElimuNeural",
#         "en-TZ-ImaniNeural",
#         "en-GB-LibbyNeural",
#         "en-GB-MaisieNeural",
#         "en-GB-RyanNeural",
#         "en-GB-SoniaNeural",
#         "en-GB-ThomasNeural",
#         "en-US-AnaNeural",
#         "en-US-AriaNeural",
#         "en-US-ChristopherNeural",
#         "en-US-EricNeural",
#         "en-US-GuyNeural",
#         "en-US-JennyNeural",
#         "en-US-MichelleNeural",
#         "en-US-RogerNeural",
#         "en-US-SteffanNeural"
#     ],
#     "fr": [
#         "No",
#         "fr-BE-CharlineNeural",
#         "fr-BE-GerardNeural",
#         "fr-CA-ThierryNeural",
#         "fr-CA-AntoineNeural",
#         "fr-CA-JeanNeural",
#         "fr-CA-SylvieNeural",
#         "fr-FR-VivienneMultilingualNeural",
#         "fr-FR-RemyMultilingualNeural",
#         "fr-FR-DeniseNeural",
#         "fr-FR-EloiseNeural",
#         "fr-FR-HenriNeural",
#         "fr-CH-ArianeNeural",
#         "fr-CH-FabriceNeural"
#     ],
#     "de": [
#         "No",
#         "de-AT-IngridNeural",
#         "de-AT-JonasNeural",
#         "de-DE-SeraphinaMultilingualNeural",
#         "de-DE-FlorianMultilingualNeural",
#         "de-DE-AmalaNeural",
#         "de-DE-ConradNeural",
#         "de-DE-KatjaNeural",
#         "de-DE-KillianNeural",
#         "de-CH-JanNeural",
#         "de-CH-LeniNeural"
#     ],
#     "hi": [
#         "No",
#         "hi-IN-MadhurNeural",
#         "hi-IN-SwaraNeural"
#     ],
#     "hu": [
#         "No",
#         "hu-HU-NoemiNeural",
#         "hu-HU-TamasNeural"
#     ],
#     "id": [
#         "No",
#         "id-ID-ArdiNeural",
#         "id-ID-GadisNeural"
#     ],
#     "it": [
#         "No",
#         "it-IT-GiuseppeNeural",
#         "it-IT-DiegoNeural",
#         "it-IT-ElsaNeural",
#         "it-IT-IsabellaNeural"
#     ],
#     "ja": [
#         "No",
#         "ja-JP-KeitaNeural",
#         "ja-JP-NanamiNeural"
#     ],
#     "kk": [
#         "No",
#         "kk-KZ-AigulNeural",
#         "kk-KZ-DauletNeural"
#     ],
#     "ko": [
#         "No",
#         "ko-KR-HyunsuNeural",
#         "ko-KR-InJoonNeural",
#         "ko-KR-SunHiNeural"
#     ],
#     "ms": [
#         "No",
#         "ms-MY-OsmanNeural",
#         "ms-MY-YasminNeural"
#     ],
#     "pl": [
#         "No",
#         "pl-PL-MarekNeural",
#         "pl-PL-ZofiaNeural"
#     ],
#     "pt": [
#         "No",
#         "pt-BR-ThalitaNeural",
#         "pt-BR-AntonioNeural",
#         "pt-BR-FranciscaNeural",
#         "pt-PT-DuarteNeural",
#         "pt-PT-RaquelNeural"
#     ],
#     "ru": [
#         "No",
#         "ru-RU-DmitryNeural",
#         "ru-RU-SvetlanaNeural"
#     ],
#     "es": [
#         "No",
#         "es-AR-ElenaNeural",
#         "es-AR-TomasNeural",
#         "es-BO-MarceloNeural",
#         "es-BO-SofiaNeural",
#         "es-CL-CatalinaNeural",
#         "es-CL-LorenzoNeural",
#         "es-ES-XimenaNeural",
#         "es-CO-GonzaloNeural",
#         "es-CO-SalomeNeural",
#         "es-CR-JuanNeural",
#         "es-CR-MariaNeural",
#         "es-CU-BelkysNeural",
#         "es-CU-ManuelNeural",
#         "es-DO-EmilioNeural",
#         "es-DO-RamonaNeural",
#         "es-EC-AndreaNeural",
#         "es-EC-LuisNeural",
#         "es-SV-LorenaNeural",
#         "es-SV-RodrigoNeural",
#         "es-GQ-JavierNeural",
#         "es-GQ-TeresaNeural",
#         "es-GT-AndresNeural",
#         "es-GT-MartaNeural",
#         "es-HN-CarlosNeural",
#         "es-HN-KarlaNeural",
#         "es-MX-DaliaNeural",
#         "es-MX-JorgeNeural",
#         "es-NI-FedericoNeural",
#         "es-NI-YolandaNeural",
#         "es-PA-MargaritaNeural",
#         "es-PA-RobertoNeural",
#         "es-PY-MarioNeural",
#         "es-PY-TaniaNeural",
#         "es-PE-AlexNeural",
#         "es-PE-CamilaNeural",
#         "es-PR-KarinaNeural",
#         "es-PR-VictorNeural",
#         "es-ES-AlvaroNeural",
#         "es-ES-ElviraNeural",
#         "es-US-AlonsoNeural",
#         "es-US-PalomaNeural",
#         "es-UY-MateoNeural",
#         "es-UY-ValentinaNeural",
#         "es-VE-PaolaNeural",
#         "es-VE-SebastianNeural"
#     ],
#     "sv": [
#         "No",
#         "sv-SE-MattiasNeural",
#         "sv-SE-SofieNeural"
#     ],
#     "th": [
#         "No",
#         "th-TH-NiwatNeural",
#         "th-TH-PremwadeeNeural"
#     ],
#     "tr": [
#         "No",
#         "tr-TR-AhmetNeural",
#         "tr-TR-EmelNeural"
#     ],
#     "uk": [
#         "No",
#         "uk-UA-OstapNeural",
#         "uk-UA-PolinaNeural"
#     ],
#     "vi": [
#         "No",
#         "vi-VN-HoaiMyNeural",
#         "vi-VN-NamMinhNeural"
#     ]
# }