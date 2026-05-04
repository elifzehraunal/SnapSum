import pytesseract
import cv2
import os
from pathlib import Path

# FATMA: Make sure this path matches your Tesseract installation folder!
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_and_extract(image_filename):
    """
    Fatma's Task: Pre-process the image and extract text.
    """
    if not os.path.exists(image_filename):
        return "Error: Image file not found!"

    # Load image 
    image = cv2.imread(image_filename)
    
    # Convert to grayscale for better accuracy 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # OCR Process (Turkish and English) 
    extracted_text = pytesseract.image_to_string(gray, lang='tur+eng')
    return extracted_text

# TEST RUN:
# print(process_and_extract('test_page.jpg'))
# Bu kısım Fatma'nın sunumda sonucu göstermesini sağlar
if __name__ == "__main__":
    image_to_test = str(Path(__file__).resolve().parents[1] / "test_page.jpeg")
    print("SnapSum OCR is processing...")
    result = process_and_extract(image_to_test)
    
    print("\n--- Extracted Text ---")
    print(result)
    print("----------------------")
