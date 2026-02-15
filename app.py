import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import re
from PIL import Image

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

st.markdown("""
<style>
.main-title{
    font-size:32px;
    font-weight:700;
    color:#0b5394;
}
.box{
    background:#f7f9fc;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✈️ Amadeus Auto PNR Builder</div>', unsafe_allow_html=True)
st.caption("Developed by Aamir Khan")

# ---------------- NAME CLEAN FIX ----------------
def clean_name(text):

    if not text:
        return ""

    text = text.replace("<", " ")
    text = re.sub(r'[^A-Z ]', '', text.upper())
    text = " ".join(text.split())

    words = text.split()
    cleaned_words = []

    for w in words:
        w = re.sub(r'(.)\1{2,}$', r'\1', w)
        cleaned_words.append(w)

    return " ".join(cleaned_words)

# ---------------- DATE FIX ----------------
def mrz_date_fix(d):

    if not d or len(d) < 6:
        return None

    try:
        y = int(d[:2])
        m = int(d[2:4])
        day = int(d[4:6])

        year = 1900 + y if y > 30 else 2000 + y
        return datetime.date(year, m, day)
    except:
        return None


def calculate_age(d):

    birth = mrz_date_fix(d)
    if not birth:
        return None, ""

    today = datetime.date.today()
    age = today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

    return age, birth.strftime("%d%b%y").upper()


# ---------------- TITLE ----------------
def passenger_title(age, gender):

    if age is None:
        return "MR"

    if age < 2:
        return "INF"
    elif age < 12:
        return "CHD"

    if gender == "F":
        return "MRS"
    return "MR"


# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Passport Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    passengers = []
    seen = set()

    for file in uploaded_files:

        img = Image.open(file)
        mrz = read_mrz(img)

        if not mrz:
            continue

        data = mrz.to_dict()

        surname = clean_name(data.get("surname"))
        given = clean_name(data.get("names"))

        passport = data.get("number")
        dob_raw = data.get("date_of_birth")
        expiry_raw = data.get("expiration_date")
        gender = data.get("sex")

        age, dob = calculate_age(dob_raw)
        title = passenger_title(age, gender)

        expiry = ""
        exp = mrz_date_fix(expiry_raw)
        if exp:
            expiry = exp.strftime("%d%b%y").upper()

        key = passport + dob
        if key in seen:
            continue
        seen.add(key)

        passengers.append({
            "surname": surname,
            "given": given,
            "title": title,
            "passport": passport,
            "dob": dob,
            "expiry": expiry,
            "father": "",
            "pob": "",
            "cnic": ""
        })

    # ---------------- DISPLAY ----------------
    st.subheader("Extracted Passport Details")

    for i,p in enumerate(passengers,1):

        st.markdown(f"""
        <div class="box">
        <b>Passenger {i}: {p['surname']} {p['given']}</b><br><br>

        Surname: {p['surname']}<br>
        Given Name: {p['given']}<br>
        Title: {p['title']}<br>
        Passport: {p['passport']}<br>
        DOB: {p['dob']}<br>
        Expiry: {p['expiry']}<br>
        Father/Husband Name: {p['father']}<br>
        Place of Birth: {p['pob']}<br>
        CNIC: {p['cnic']}
        </div>
        """, unsafe_allow_html=True)

    # ---------------- NM1 ----------------
    st.subheader("NM1 Entries")

    nm1_lines = []
    for p in passengers:
        nm1 = f"NM1{p['surname']}/{p['given']} {p['title']}"
        nm1_lines.append(nm1)

    st.code("\n".join(nm1_lines))

    # ---------------- SRDOCS ----------------
    st.subheader("SRDOCS Entries")

    docs_lines = []
    for i,p in enumerate(passengers,1):

        docs = (
            f"SRDOCS SV HK1-P-PK-{p['passport']}-"
            f"PK-{p['dob']}-{p['title'][0]}-{p['expiry']}-"
            f"{p['surname']}-{p['given'].replace(' ','-')}-H/P{i}"
        )
        docs_lines.append(docs)

    st.code("\n".join(docs_lines))
