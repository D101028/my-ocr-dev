import requests

from config import Config

def ocr(img_path: str, api: str = Config.OCR_SERVER_API) -> str:
    try:
        with open(img_path, 'rb') as f:
            files = {'file': f}
            resp = requests.post(api, files=files)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"\n✓ OCR completed for: {img_path}")
            print(f"Recognized texts: {result['rec_texts']}")
            return "\n".join(result['rec_texts'])
        else:
            print(f"✗ OCR failed with status {resp.status_code}: {resp.text}")
            return ""
    except Exception as e:
        print(f"✗ Error during OCR: {str(e)}")
        return ""
