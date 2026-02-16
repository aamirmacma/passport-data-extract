import streamlit as st
import pytesseract
import cv2
import numpy as np
import re
import tempfile
import os


# ==============================
# TESSERACT PATH
# ==============================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ==============================
# CLEAN TEXT FUNCTION
# ==============================
def clean_text(t):
    if not t:
        return ""
    t = t.replace("|", "")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# ==============================
# FIELD FINDER
# ==============================
def find_value(text, label):

    pattern = rf"{label}\s*[:\-]?\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        value = match.group(1)
        value = value.split("\n")[0]
        return clean_text(value)

    return ""


# ==============================
# CNIC FINDER
# ==============================
def extract_cnic(text):

    match = re.search(r"\d{5}-\d{7}-\d", text)
    if match:
        return match.group()
    return ""


# ==============================
# DATE FINDER
# ==============================
def extract_date(text, label):

    pattern = rf"{label}.*?(\d{{1,2}}\s+[A-Z]{{3}}\s+\d{{4}})"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1)

    return ""


# ==============================
# MAIN RUN FUNCTION
# ==============================
def run():

    st.title("🕋 Hajj Form Extractor")

    file = st.file_uploader(
        "Upload Hajj Booking Form (JPG/PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if not file:
        return

    # save temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(file.getbuffer())
        path = tmp.name

    img = cv2.imread(path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5)
    gray = cv2.GaussianBlur(gray, (3,3), 0)

    text = pytesseract.image_to_string(gray).upper()

    # ==============================
    # APPLICANT DATA
    # ==============================
    name = find_value(text, "NAME OF APPLICANT")
    father = find_value(text, "FATHER / HUSBAND NAME")
    passport = find_value(text, "PASSPORT NO")
    occupation = find_value(text, "OCCUPATION")
    country_stay = find_value(text, "COUNTRY STAY IN")

    dob = extract_date(text, "DATE OF BIRTH")
    issue = extract_date(text, "DATE OF ISSUE")
    expiry = extract_date(text, "DATE OF EXPIRY")

    cnic = extract_cnic(text)

    # ==============================
    # NOMINEE DATA
    # ==============================
    nominee_name = find_value(text, "NAME OF NOMINEE")
    nominee_relation = find_value(text, "NOMINEE RELATION")
    nominee_cnic = extract_cnic(text.split("NOMINEE")[-1])

    nominee_mobile = find_value(text, "MOBILE / WHATSAPP")

    # ==============================
    # OUTPUT
    # ==============================
    st.subheader("Applicant Details")

    st.table({
        "Field": [
            "Applicant Name",
            "Father / Husband",
            "CNIC",
            "Date of Birth",
            "Passport No",
            "Date of Issue",
            "Date of Expiry",
            "Occupation",
            "Country Stay"
        ],
        "Value": [
            name,
            father,
            cnic,
            dob,
            passport,
            issue,
            expiry,
            occupation,
            country_stay
        ]
    })

    st.subheader("Nominee Details")

    st.table({
        "Field": [
            "Nominee Name",
            "Relation",
            "CNIC",
            "Mobile"
        ],
        "Value": [
            nominee_name,
            nominee_relation,
            nominee_cnic,
            nominee_mobile
        ]
    })

    os.remove(path)
