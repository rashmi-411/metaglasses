import easyocr
import os

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])  # English

# Check what image files exist
current_dir = os.listdir('.')
image_files = [f for f in current_dir if f.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp'))]

if image_files:
    # Use the first available image
    #image_path = image_files[0]
    image_path = "C:\Users\LENOVO\OneDrive\Desktop\drublet\image.png"  # specify your image file here
    print(f"Using image: {image_path}")
    
    # Perform text recognition
    results = reader.readtext(image_path)
    
    # Print results
    for (bbox, text, confidence) in results:
        print(f"Text: {text} | Confidence: {confidence:.2f}")
else:
    print("No image files found in directory. Please add an image file.")