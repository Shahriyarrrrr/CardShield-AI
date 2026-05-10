import easyocr

reader = easyocr.Reader(['en'])

image_path = "dataset/images/test/cc_0.jpg"

results = reader.readtext(image_path)

print("\n===== OCR RESULTS =====\n")

for result in results:
    bbox, text, confidence = result

    print(f"Detected Text : {text}")
    print(f"Confidence    : {confidence:.2f}")
    print("-" * 40)