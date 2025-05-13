from enum import Enum

class TranslationType(Enum):
    GOOGLE = 0                  # Google Translate
    MICROSOFT = 1               # Microsoft Translate
    AI302 = 2                   # 302.AI
    BAIDU = 3                   # Baidu Translate
    DEEPL = 4                   # DeepL
    DEEPLX = 5                  # DeepLx
    OFFLINE_OTT = 6             # Offline Translation OTT
    TENCENT = 7                 # Tencent Translate
    OPENAI_CHATGPT = 8          # OpenAI ChatGPT
    LOCAL_LLM = 9               # Local Large Model and Compatible AI
    BYTE_VOLCANO = 10           # Byte Volcano Engine
    AZURE_GPT = 11              # AzureAI GPT
    GEMINI = 12                 # Gemini
    CUSTOM_API = 13             # Custom Translation API
    FREE_GOOGLE = 14            # FreeGoogle Translate
