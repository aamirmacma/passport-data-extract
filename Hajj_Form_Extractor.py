import streamlit as st
import pytesseract
import cv2
import numpy as np
import re
import os
import uuid

# ==============================
# TESSERACT PATH
# ==============================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ==========================================
# TEXT FINDER FUNCTION
# ==========================================
def find_value(text, label):

    pattern = rf"{label}\s*(.*)"
    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    return ""


# ==========================================
# MAIN RUN FUNCTION
# ==========================================
def run():

    st.title("🕋 Hajj Booking Form Extractor")

    uploaded = st.file_uploader(
        "Upload Hajj Booking Form (JPG)",
        type=["jpg", "jpeg", "png"]
    )

    if not uploaded:
        return

    temp = f"temp_{uuid.uuid4().hex}.jpg"

    with open(temp, "wb") as f:
        f.write(uploaded.getbuffer())

    img = cv2.imread(temp)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    text = pytesseract.image_to_string(gray).upper()

    os.remove(temp)

    # ==========================
    # FIELD EXTRACTION
    # ==========================

    data = {}

    data["Name"] = find_value(text, "NAME OF APPLICANT")
    data["Father/Husband"] = find_value(text, "FATHER")
    data["CNIC"] = re.search(r"\d{5}-\d{7}-\d", text)
    data["Passport"] = re.search(r"[A-Z]{2}\d{7}", text)
    data["DOB"] = find_value(text, "DATE OF BIRTH")
    data["Mobile"] = find_value(text, "MOBILE")
    data["WhatsApp"] = find_value(text, "WHATSAPP")
    data["Address"] = find_value(text, "RESIDENT ADDRESS")

    if data["CNIC"]:
        data["CNIC"] = data["CNIC"].group()
    else:
        data["CNIC"] = ""

    if data["Passport"]:
        data["Passport"] = data["Passport"].group()
    else:
        data["Passport"] = ""

    # ==========================
    # OUTPUT
    # ==========================

    st.subheader("Extracted Hajj Form Data")

    for k, v in data.items():
        st.markdown(f"**{k}:** {v}")
