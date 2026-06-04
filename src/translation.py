from deep_translator import GoogleTranslator

def translate_text(text, api_key=None, target_lang="EN"):
    if api_key and api_key != "YOUR_DEEPL_API_KEY" and api_key.strip() != "":
        import requests
        url = "https://api-free.deepl.com/v2/translate"
        headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
        data = {"text": [text], "target_lang": target_lang.upper()}
        try:
            response = requests.post(url, headers=headers, data=data)
            return response.json()["translations"][0]["text"]
        except Exception as e:
            pass # 실패 시 구글 번역으로 넘어감
    try:
        # deep-translator는 언어 코드를 소문자로 받으므로 변환 (예: EN -> en)
        lang_map = {"EN": "en", "KO": "ko", "JA": "ja", "ZH": "zh-CN"}
        dest_lang = lang_map.get(target_lang.upper(), "en")
        
        translated = GoogleTranslator(source='auto', target=dest_lang).translate(text)
        return translated
    except Exception as e:
        return f"[Error] {text}"