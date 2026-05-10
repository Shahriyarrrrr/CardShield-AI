from ultralytics import YOLO
import easyocr
import cv2
import re

# =========================
# LUHN VALIDATION FUNCTION
# =========================

def luhn_check(card_number):

    card_number = card_number.replace(" ", "")

    if not card_number.isdigit():
        return False

    total = 0
    reverse_digits = card_number[::-1]

    for index, digit in enumerate(reverse_digits):

        n = int(digit)

        if index % 2 == 1:
            n = n * 2

            if n > 9:
                n = n - 9

        total += n

    return total % 10 == 0


# =========================
# LOAD AI MODELS
# =========================

model = YOLO("runs/detect/train-5/weights/best.pt")

reader = easyocr.Reader(['en'])

# =========================
# IMAGE PATH
# =========================

image_path = "dataset/images/test/cc_2.jpg"

# =========================
# YOLO DETECTION
# =========================

results = model.predict(
    source=image_path,
    conf=0.25,
    save=True
)

# =========================
# OCR EXTRACTION
# =========================

image = cv2.imread(image_path)

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

ocr_results = reader.readtext(image_rgb)

print("\n===================================")
print("ULTIMATE AI FRAUD ANALYSIS REPORT")
print("===================================\n")

detected_texts = []

for result in ocr_results:

    bbox, text, confidence = result

    if confidence > 0.30:

        detected_texts.append(text)

        print(f"TEXT: {text}")
        print(f"CONFIDENCE: {confidence:.2f}")
        print("-----------------------------------")

# =========================
# CARD NUMBER RECONSTRUCTION
# =========================

possible_card_numbers = []

combined_digits = ""

for text in detected_texts:

    cleaned = re.sub(r'[^0-9]', '', text)

    if len(cleaned) >= 4:
        combined_digits += cleaned

# GENERATE POSSIBLE CARD NUMBERS
for i in range(len(combined_digits)):

    for length in range(12, 20):

        possible = combined_digits[i:i+length]

        if len(possible) == length:
            possible_card_numbers.append(possible)

# REMOVE DUPLICATES
possible_card_numbers = list(set(possible_card_numbers))

# =========================
# FRAUD ANALYSIS
# =========================

fraud_score = 0

all_text = " ".join(detected_texts).upper()

print("\n===================================")
print("CARD VALIDATION CHECKS")
print("===================================\n")

# =========================
# CHECK CARD PROVIDER
# =========================

provider_detected = False

if "VISA" in all_text:
    print("CARD PROVIDER: VISA")
    provider_detected = True

elif "MASTERCARD" in all_text:
    print("CARD PROVIDER: MASTERCARD")
    provider_detected = True

if not provider_detected:
    print("WARNING: No valid provider detected.")
    fraud_score += 1

# =========================
# CARD NUMBER VALIDATION
# =========================

valid_card_found = False

if len(possible_card_numbers) == 0:

    print("\nWARNING: No possible card number detected.")
    fraud_score += 1

else:

    print("\nPOSSIBLE CARD NUMBERS:")
    print("----------------------")

    for number in possible_card_numbers:

        if luhn_check(number):

            print(f"{number} --> VALID")
            valid_card_found = True
            break

    if not valid_card_found:

        print("No valid card number detected.")
        fraud_score += 1

# =========================
# EXPIRY DATE CHECK
# =========================

expiry_found = False

expiry_pattern = r"(0[1-9]|1[0-2])\/([0-9]{2})"

for text in detected_texts:

    if re.search(expiry_pattern, text):
        expiry_found = True
        print("\nVALID EXPIRY DATE DETECTED")
        break

if not expiry_found:
    print("\nWARNING: Expiry date missing.")
    fraud_score += 1

# =========================
# CARDHOLDER NAME CHECK
# =========================

name_found = False

for text in detected_texts:

    words = text.split()

    if len(words) >= 2 and text.replace(" ", "").replace(".", "").isalpha():
        name_found = True
        print("CARDHOLDER NAME DETECTED")
        break

if not name_found:
    print("WARNING: Cardholder name unclear.")
    fraud_score += 1

# =========================
# FINAL RESULT
# =========================

print("\n===================================")

if fraud_score == 0:
    print("FINAL RESULT: CARD APPEARS LEGITIMATE")

elif fraud_score == 1:
    print("FINAL RESULT: CARD LOOKS SUSPICIOUS")

else:
    print("FINAL RESULT: POSSIBLE FAKE CARD DETECTED")

print("===================================\n")