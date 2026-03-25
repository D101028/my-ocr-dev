import requests
import json
from pathlib import Path

# Server configuration
SERVER_URL = "http://127.0.0.1:11451"
SERVER_PORT = 11451

def health_check():
    """
    Check if the OCR server is running and healthy
    """
    try:
        resp = requests.get(f"{SERVER_URL}/health")
        if resp.status_code == 200:
            print("✓ Server is healthy")
            return True
        else:
            print("✗ Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {SERVER_URL}")
        return False

def ocr_from_path(image_path):
    """
    Perform OCR on an image file using file path
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: OCR results containing recognized text
    """
    try:
        payload = {"path": image_path}
        resp = requests.post(f"{SERVER_URL}/ocr", json=payload)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"\n✓ OCR completed for: {image_path}")
            print(f"Recognized texts: {result['rec_texts']}")
            return result
        else:
            print(f"✗ OCR failed with status {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        print(f"✗ Error during OCR: {str(e)}")
        return None

def ocr_from_file(image_file_path):
    """
    Perform OCR on an image file using file upload
    
    Args:
        image_file_path (str): Path to the image file to upload
        
    Returns:
        dict: OCR results containing recognized text
    """
    try:
        # Check if file exists
        if not Path(image_file_path).exists():
            print(f"✗ File not found: {image_file_path}")
            return None
        
        with open(image_file_path, 'rb') as f:
            files = {'file': f}
            resp = requests.post(f"{SERVER_URL}/ocr", files=files)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"\n✓ OCR completed for uploaded file: {image_file_path}")
            print(f"Recognized texts: {result['rec_texts']}")
            return result
        else:
            print(f"✗ OCR failed with status {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        print(f"✗ Error during OCR: {str(e)}")
        return None

def main():
    """
    Main function demonstrating various usage examples
    """
    print("=" * 60)
    print("PaddleOCR Server - Usage Examples")
    print("=" * 60)
    
    # Step 1: Health check
    print("\n1. Health Check")
    print("-" * 60)
    if not health_check():
        print("\nPlease start the server first:")
        print("  python server.py")
        return
    
    # Step 2: OCR from file path
    print("\n2. OCR from File Path")
    print("-" * 60)
    result1 = ocr_from_path("./test2.png")
    if result1:
        print(f"Input path: {result1['input_path']}")
    
    # Step 3: OCR from file upload
    print("\n3. OCR from File Upload")
    print("-" * 60)
    # Make sure test2.png exists before uploading
    if Path("./test2.png").exists():
        result2 = ocr_from_file("./test2.png")
        if result2:
            print(f"Input path: {result2['input_path']}")
    else:
        print("✗ test2.png not found for upload example")
    
    # Step 4: Batch processing
    print("\n4. Batch Processing")
    print("-" * 60)
    test_images = ["./test.png", "./test2.png"]
    results = []
    
    for image_path in test_images:
        if Path(image_path).exists():
            result = ocr_from_path(image_path)
            if result:
                results.append(result)
        else:
            print(f"⊘ Skipping {image_path} (not found)")
    
    # Save results
    if results:
        output_file = "ocr_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()