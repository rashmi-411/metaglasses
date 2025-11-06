import pytesseract
from PIL import Image

# Optional: specify tesseract path if not added to system PATH
# Uncomment and edit the below line if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR"""
    try:
        # Open the image
        img = Image.open(image_path)

        # Perform OCR
        text = pytesseract.image_to_string(img)

        # Return extracted text
        return text.strip()

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("🔍 OCR Text Extraction Tool")
    image_path = input("Enter the image file path: ").strip()

    result = extract_text_from_image(image_path)
    
    print("\n📄 Extracted Text:\n")
    print(result if result else "No text detected.")
