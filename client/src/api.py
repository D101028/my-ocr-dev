import requests

from config import Config

def ocr(img_path: str, api: str = Config.OCR_SERVER_API, session: requests.Session | None=None) -> str:
    """
    :param session: 傳入 requests.Session() 實例以便外部控制
    """
    try:
        # 如果沒有傳入 session，則使用全域 requests (可能會無法中斷)
        client = session if session else requests

        with open(img_path, 'rb') as f:
            img_data = f.read()
        
        files = {'file': ('image.png', img_data)}
        resp = client.post(api, files=files, timeout=15)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"\n✓ OCR completed for: {img_path}")
            return "\n".join(result.get('rec_texts', [])).strip()
        else:
            print(f"✗ OCR failed with status {resp.status_code}")
            return resp.content.decode("utf-8")
    except (requests.exceptions.RequestException, Exception) as e:
        raise e