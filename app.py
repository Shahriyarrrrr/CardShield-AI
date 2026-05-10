import streamlit as st
import easyocr
import cv2
import numpy as np
import re
from PIL import Image
from ultralytics import YOLO

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="CardShield-AI",
    page_icon="💳",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

html, body, [class*="css"]  {
    background-color: #0b1220;
    color: white;
    font-family: 'Segoe UI';
}

.main-title {
    font-size: 48px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 20px;
    color: #9ca3af;
    margin-bottom: 30px;
}

.section-card {
    background-color: #111827;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

.metric-box {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #334155;
}

.metric-title {
    color: #94a3b8;
    font-size: 15px;
}

.metric-value {
    color: white;
    font-size: 28px;
    font-weight: bold;
}

.success-box {
    background-color: rgba(16,185,129,0.15);
    border: 1px solid #10b981;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
}

.warning-box {
    background-color: rgba(245,158,11,0.15);
    border: 1px solid #f59e0b;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
}

.danger-box {
    background-color: rgba(239,68,68,0.15);
    border: 1px solid #ef4444;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
}

.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    background-color: #2563eb;
    color: white;
    border: none;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# HEADER
# =========================================

st.markdown("""
<div class="main-title">💳 CardShield-AI</div>
<div class="sub-title">
Enterprise Grade AI Credit Card Fraud Detection System
</div>
""", unsafe_allow_html=True)

# =========================================
# LOAD MODELS
# =========================================

@st.cache_resource
def load_models():
    model = YOLO("models/best.pt")
    reader = easyocr.Reader(['en'])
    return model, reader

model, reader = load_models()

# =========================================
# LUHN VALIDATION
# =========================================

def luhn_check(card_number):

    card_number = card_number.replace(" ", "")

    if not card_number.isdigit():
        return False

    total = 0
    reverse_digits = card_number[::-1]

    for index, digit in enumerate(reverse_digits):

        n = int(digit)

        if index % 2 == 1:
            n *= 2

            if n > 9:
                n -= 9

        total += n

    return total % 10 == 0

# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.title("⚙️ System Panel")

    st.markdown("---")

    st.write("### AI Modules")

    st.success("YOLOv8 Detection")
    st.success("EasyOCR Engine")
    st.success("Luhn Validator")
    st.success("Fraud Analyzer")

    st.markdown("---")

    st.write("### System Status")

    st.success("System Online")

# =========================================
# FILE UPLOAD
# =========================================

uploaded_file = st.file_uploader(
    "Upload Card Image",
    type=["jpg", "jpeg", "png"]
)

# =========================================
# MAIN PROCESS
# =========================================

if uploaded_file is not None:

    with st.spinner("Analyzing Card Image..."):

        image = Image.open(uploaded_file)

        image_np = np.array(image)

        # =========================================
        # YOLO DETECTION
        # =========================================

        results = model.predict(
            source=image_np,
            conf=0.25
        )

        annotated_frame = results[0].plot()

        # =========================================
        # OCR EXTRACTION
        # =========================================

        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

        ocr_results = reader.readtext(image_rgb)

        detected_texts = []

        for result in ocr_results:

            bbox, text, confidence = result

            if confidence > 0.30:
                detected_texts.append(text)

        # =========================================
        # CARD NUMBER EXTRACTION
        # =========================================

        combined_digits = ""

        for text in detected_texts:

            cleaned = re.sub(r'[^0-9]', '', text)

            if len(cleaned) >= 4:
                combined_digits += cleaned

        possible_card_numbers = []

        for i in range(len(combined_digits)):

            for length in range(12, 20):

                possible = combined_digits[i:i+length]

                if len(possible) == length:
                    possible_card_numbers.append(possible)

        possible_card_numbers = list(set(possible_card_numbers))

        # =========================================
        # FRAUD ANALYSIS
        # =========================================

        fraud_score = 0

        all_text = " ".join(detected_texts).upper()

        provider = "Unknown"

        if "VISA" in all_text:
            provider = "VISA"

        elif "MASTERCARD" in all_text:
            provider = "MASTERCARD"

        else:
            fraud_score += 1

        valid_card_found = False
        valid_number = None

        for number in possible_card_numbers:

            if luhn_check(number):

                valid_card_found = True
                valid_number = number
                break

        if not valid_card_found:
            fraud_score += 1

        expiry_found = False

        expiry_pattern = r"(0[1-9]|1[0-2])\/([0-9]{2})"

        for text in detected_texts:

            if re.search(expiry_pattern, text):

                expiry_found = True
                break

        if not expiry_found:
            fraud_score += 1

        name_found = False

        for text in detected_texts:

            words = text.split()

            if len(words) >= 2 and text.replace(" ", "").replace(".", "").isalpha():

                name_found = True
                break

        if not name_found:
            fraud_score += 1

        # =========================================
        # DASHBOARD METRICS
        # =========================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Card Provider</div>
                <div class="metric-value">{provider}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">OCR Text Found</div>
                <div class="metric-value">{len(detected_texts)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Fraud Score</div>
                <div class="metric-value">{fraud_score}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            status = "SAFE"

            if fraud_score == 1:
                status = "SUSPICIOUS"

            elif fraud_score >= 2:
                status = "DANGER"

            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Risk Status</div>
                <div class="metric-value">{status}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================================
        # IMAGE DISPLAY
        # =========================================

        left, right = st.columns(2)

        with left:

            st.markdown("""
            <div class="section-card">
            <h3>Uploaded Card</h3>
            </div>
            """, unsafe_allow_html=True)

            st.image(image, use_container_width=True)

        with right:

            st.markdown("""
            <div class="section-card">
            <h3>AI Detection Result</h3>
            </div>
            """, unsafe_allow_html=True)

            st.image(annotated_frame, use_container_width=True)

        # =========================================
        # OCR RESULTS
        # =========================================

        st.markdown("""
        <div class="section-card">
        <h3>OCR Extracted Text</h3>
        </div>
        """, unsafe_allow_html=True)

        for text in detected_texts:
            st.write(f"• {text}")

        # =========================================
        # VALIDATION RESULTS
        # =========================================

        st.markdown("""
        <div class="section-card">
        <h3>Validation Results</h3>
        </div>
        """, unsafe_allow_html=True)

        if valid_card_found:

            st.markdown(f"""
            <div class="success-box">
            ✅ Valid Card Number Detected<br><br>
            <b>{valid_number}</b>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class="danger-box">
            ❌ No Valid Card Number Detected
            </div>
            """, unsafe_allow_html=True)

        if expiry_found:

            st.markdown("""
            <div class="success-box">
            ✅ Valid Expiry Date Found
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class="warning-box">
            ⚠️ Expiry Date Missing
            </div>
            """, unsafe_allow_html=True)

        if name_found:

            st.markdown("""
            <div class="success-box">
            ✅ Cardholder Name Detected
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class="warning-box">
            ⚠️ Cardholder Name Missing
            </div>
            """, unsafe_allow_html=True)

        # =========================================
        # FINAL RESULT
        # =========================================

        st.markdown("<br>", unsafe_allow_html=True)

        if fraud_score == 0:

            st.markdown("""
            <div class="success-box">
            <h2>✅ FINAL RESULT: CARD APPEARS LEGITIMATE</h2>
            </div>
            """, unsafe_allow_html=True)

        elif fraud_score == 1:

            st.markdown("""
            <div class="warning-box">
            <h2>⚠️ FINAL RESULT: CARD LOOKS SUSPICIOUS</h2>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class="danger-box">
            <h2>🚨 FINAL RESULT: POSSIBLE FAKE CARD DETECTED</h2>
            </div>
            """, unsafe_allow_html=True)

# =========================================
# FOOTER
# =========================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<center>
<span style='color:gray'>
CardShield-AI © 2026 | Enterprise Fraud Detection Platform
</span>
</center>
""", unsafe_allow_html=True)