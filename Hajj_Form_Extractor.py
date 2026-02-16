import streamlit as st
import pytesseract
import cv2
import numpy as np
import tempfile
import os
import re


# =========================
# TESSERACT PATH
# =========================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# IMAGE PREPROCESS
# =========================
def preprocess(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # sharpen
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    gray = cv2.filter2D(gray, -1, kernel)

    gray = cv2.resize(gray, None, fx=1.5, fy=1.5)
    gray = cv2.GaussianBlur(gray,(3,3),0)

    return gray


# =========================
# CLEAN TEXT
# =========================
def clean_line(line):

    line = line.replace("|", "")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


# =========================
# FULL TEXT PARSER
# =========================
def extract_all_fields(text):

    data = {}

    lines = [clean_line(l) for l in text.split("\n") if l.strip()]

    last_label = ""

    for line in lines:

        # detect label style line
        if ":" in line:
            parts = line.split(":",1)
            label = parts[0].strip()
            value = parts[1].strip()

            data[label] = value
            last_label = label

        else:
            # sometimes value comes next line
            if last_label and last_label in data and data[last_label] == "":
                data[last_label] = line

    return data, lines


# =========================
# MAIN RUN
# =========================
def run():

    st.title("🕋 Hajj Form Full Extractor")

    file = st.file_uploader(
        "Upload Hajj Booking Form",
        type=["jpg","jpeg","png"]
    )

    if not file:
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(file.getbuffer())
        path = tmp.name

    img = cv2.imread(path)
    processed = preprocess(img)

    # FULL OCR
    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    text = text.upper()

    data, lines = extract_all_fields(text)

    # =========================
    # OUTPUT 1 : STRUCTURED TABLE
    # =========================
    st.subheader("Extracted Form Fields")

    if data:
        st.table({
            "Field": list(data.keys()),
            "Value": list(data.values())
        })

    # =========================
    # OUTPUT 2 : FULL TEXT (NO LOSS)
    # =========================
    st.subheader("Full Extracted Text (Nothing Missing)")

    st.code("\n".join(lines))

    os.remove(path)
