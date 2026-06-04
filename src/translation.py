import requests

def translate_text(text, api_key=None, target_lang="EN"):
    """
    DeepL API를 사용하여 번역합니다. API 키가 없으면 임시 텍스트를 반환합니다.
    """
    if not api_key or api_key == "YOUR_DEEPL_API_KEY":
        return f"[TR] {text}"
    
    url = "https://api-free.deepl.com/v2/translate"
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
    data = {"text": [text], "target_lang": target_lang}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.json()["translations"][0]["text"]
    except Exception as e:
        return f"[Error] {text}"
