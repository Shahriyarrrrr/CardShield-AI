from ultralytics import YOLO
import easyocr
import cv2

# LOAD YOLO MODEL
model = YOLO("runs/detect/train-5/weights/best.pt")

# LOAD OCR
reader = easyocr.Reader(['en'])

# IMAGE PATH
image_path = "dataset/images/test/cc_1.jpg"

# RUN CARD DETECTION
results = model.predict(
    source=image_path,
    conf=0.25,
    save=True
)

print("\n==============================")
print("CARD FRAUD ANALYSIS REPORT")
print("==============================\n")

# READ IMAGE USING OPENCV
image = cv2.imread(image_path)

# CONVERT IMAGE TO RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# OCR
ocr_results = reader.readtext(image_rgb)

detected_texts = []

print("DETECTED TEXT:")
print("------------------")

for result in ocr_results:
    bbox, text, confidence = result

    if confidence > 0.30:
        detected_texts.append(text)

        print(f"{text} ({confidence:.2f})")

print("\n------------------")

# FRAUD ANALYSIS
fraud_score = 0

all_text = " ".join(detected_texts).upper()

# CHECK CARD NETWORK
if "VISA" not in all_text and "MASTERCARD" not in all_text:
    print("WARNING: No valid card provider detected.")
    fraud_score += 1

# CHECK CARD NUMBER
numbers_found = False

for text in detected_texts:
    digits = ''.join(filter(str.isdigit, text))

    if len(digits) >= 12:
        numbers_found = True
        break

if not numbers_found:
    print("WARNING: Card number missing.")
    fraud_score += 1

# CHECK POSSIBLE NAME
name_found = False

for text in detected_texts:
    words = text.split()

    if len(words) >= 2:
        name_found = True
        break

if not name_found:
    print("WARNING: Cardholder name unclear.")
    fraud_score += 1

print("\n==============================")

if fraud_score == 0:
    print("RESULT: CARD APPEARS LEGITIMATE")
elif fraud_score == 1:
    print("RESULT: CARD LOOKS SUSPICIOUS")
else:
    print("RESULT: POSSIBLE FAKE CARD DETECTED")

print("==============================")