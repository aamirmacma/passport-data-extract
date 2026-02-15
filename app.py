import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import re

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Amadeus Auto PNR Builder",
    layout="wide"
)

# ================= HEADER + STYLE =================
st.markdown("""
<style>

.stApp {
    background-color: #f4f7fb;
}

/* Header */
.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    box-shadow:0 3px 8px rgba(0,0,0,0.15);
}

.header-title {
    font-size:26px;
    font-weight:700;
    color:white;
}

.header-dev {
    background:white;
    color:#0b5394;
    padding:6px 14px;
    border-radius:20px;
    font-size:14px;
    font-weight:600;
}

.passport-box {
    background:white;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #1c7ed6;
    margin-bottom:10px;
}

.nm1-box {
    background:#eef5ff;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #2f9e44;
}

.docs-box {
    background:#f1fff5;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #37b24d;
}

</style>

<div class="header-bar">
    <div class="header-title">✈️ Amadeus Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def clean_name(text):
    text = text.replace("<", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_date(mrz_date):
    try:
        dt = datetime.datetime.strptime(mrz_date, "%y%m%d")
        return dt.strftime("%d%b%y").upper()
    except:
        return ""

def calculate_age(dob):
    try:
        dob_dt = datetime.datetime.strptime(dob, "%y%m%d")
        today = datetime.datetime.today()
        return (today - dob_dt).days // 365
    except:
        return 30

def passenger_title(age, gender):
    if age < 2:
        return "INF"
    elif age < 12:
        return "MSTR" if gender == "M" else "MISS"
    else:
        return "MR" if gender == "M" else "MRS"

# ================= UPLOAD =================
uploaded_files = st.file_uploader(
    "Upload Passport Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

nm1_lines = []
docs_lines = []
seen_passports = set()

if uploaded_files:

    st.subheader("Extracted Passport Details")

    for file in uploaded_files:

        with open("temp.jpg", "wb") as f:
            f.write(file.getbuffer())

        mrz = read_mrz("temp.jpg")

        if not mrz:
            st.error(f"{file.name} - MRZ not detected")
            continue

        d = mrz.to_dict()

        passport = d.get("number", "")
        if passport in seen_passports:
            continue
        seen_passports.add(passport)

        surname = clean_name(d.get("surname", ""))
        names = clean_name(d.get("names", ""))
        gender = d.get("sex", "M")

        dob_raw = d.get("date_of_birth", "")
        exp_raw = d.get("expiration_date", "")

        dob = format_date(dob_raw)
        expiry = format_date(exp_raw)

        age = calculate_age(dob_raw)
        title = passenger_title(age, gender)

        # ===== NM1 =====
        nm1 = f"NM1{surname}/{names} {title}"
        nm1_lines.append(nm1)

        # ===== SRDOCS =====
        srdocs = (
            f"SRDOCS SV HK1-P-PAK-{passport}-PAK-"
            f"{dob}-{gender}-{expiry}-{surname}-{names}-H/P1"
        )
        docs_lines.append(srdocs)

        st.markdown('<div class="passport-box">', unsafe_allow_html=True)
        st.write(f"Passenger: {surname} {names}")
        st.write(f"Passport: {passport}")
        st.write(f"DOB: {dob}")
        st.write(f"Expiry: {expiry}")
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== NM1 DISPLAY =====
    if nm1_lines:
        st.markdown('<div class="nm1-box">', unsafe_allow_html=True)
        st.subheader("NM1 Entries")
        for line in nm1_lines:
            st.code(line)
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== SRDOCS DISPLAY =====
    if docs_lines:
        st.markdown('<div class="docs-box">', unsafe_allow_html=True)
        st.subheader("SRDOCS Entries")
        for line in docs_lines:
            st.code(line)
        st.markdown('</div>', unsafe_allow_html=True)

    if os.path.exists("temp.jpg"):
        os.remove("temp.jpg")
