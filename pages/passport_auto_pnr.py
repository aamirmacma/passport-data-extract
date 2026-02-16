import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import streamlit.components.v1 as components


# ================= TESSERACT =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ================= HEADER =================
st.markdown("""
<style>
.stApp { background:#f4f7fb; }
.header-bar{
background:linear-gradient(90deg,#0b5394,#1c7ed6);
padding:14px 20px;
border-radius:12px;
margin-bottom:20px;
display:flex;
justify-content:space-between;
align-items:center;
color:white;
font-weight:700;
font-size:24px;
}
.passport-box{
background:white;
padding:15px;
border-radius:12px;
border-left:5px solid #1c7ed6;
margin-bottom:10px;
}
</style>

<div class="header-bar">
✈️ Passport Auto PNR Builder
</div>
""", unsafe_allow_html=True)


# ================= DATE FUNCTIONS =================

def mrz_date_fix(d):
    try:
        if not d or len(str(d)) < 6:
            return None

        d = str(d)
        y = int(d[:2])
        m = int(d[2:4])
        da = int(d[4:6])

        if y > datetime.datetime.now().year % 100:
            y += 1900
        else:
            y += 2000

        return datetime.datetime(y, m, da)
    except:
        return None


def safe_date(d):
    dt = mrz_date_fix(d)
    return "" if dt is None else dt.strftime("%d%b%y").upper()


def calculate_age(d):
    birth = mrz_date_fix(d)
    if birth is None:
        return 0, ""

    today = datetime.datetime.today()
    age = today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

    return age, birth.strftime("%d%b%y").upper()


# ================= TITLE =================

def passenger_title(age, gender):
    if age >= 12:
        return "MR" if gender == "M" else "MRS"
    elif age >= 2:
        return "CHD"
    return "INF"


# ================= NAME CLEANER (FIXED) =================

def clean_word(w):
    w = w.strip()

    # remove single letters
    if len(w) <= 1:
        return False

    # remove KKKKK or same letters
    if len(set(w)) == 1:
        return False

    # remove words with too many K
    if w.count("K") > len(w) * 0.5:
        return False

    return True


def parse_mrz_names(surname, names):

    surname = surname.replace("<", "").strip().upper()

    names = names.replace("<", " ")
    words = names.split()

    clean = []
    for w in words:
        w = w.strip().upper()
        if clean_word(w):
            clean.append(w)

    return surname, " ".join(clean)


# ================= ROTATE =================

def auto_rotate(path):
    img = cv2.imread(path)
    if img is None:
        return
    h, w = img.shape[:2]
    if h > w:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite(path, img)


# ================= UPLOAD =================

files = st.file_uploader(
    "Upload Passport Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

passengers = []
seen = set()

if files:

    for f in files:

        temp = f"temp_{uuid.uuid4().hex}.jpg"

        with open(temp, "wb") as fp:
            fp.write(f.getbuffer())

        auto_rotate(temp)

        try:
            mrz = read_mrz(temp)
        except:
            mrz = None

        if not mrz:
            st.warning("MRZ not detected")
            os.remove(temp)
            continue

        d = mrz.to_dict()
        passport = d.get("number", "")

        if passport in seen:
            st.warning(f"Duplicate skipped: {passport}")
            os.remove(temp)
            continue

        seen.add(passport)

        surname, names = parse_mrz_names(
            d.get("surname", ""),
            d.get("names", "")
        )

        age, dob = calculate_age(d.get("date_of_birth"))
        exp = safe_date(d.get("expiration_date"))

        passengers.append({
            "surname": surname,
            "names": names,
            "title": passenger_title(age, d.get("sex", "M")),
            "passport": passport,
            "dob": dob,
            "exp": exp,
            "gender": d.get("sex", "M"),
            "country": d.get("country", "")
        })

        os.remove(temp)


# ================= OUTPUT =================

if passengers:

    st.subheader("Extracted Passport Details")

    nm1_lines = []
    docs_lines = []

    for i, p in enumerate(passengers, 1):

        st.markdown('<div class="passport-box">', unsafe_allow_html=True)
        st.write(f"Passenger {i}: {p['surname']} {p['names']}")
        st.write("Passport:", p["passport"])
        st.write("DOB:", p["dob"])
        st.write("Expiry:", p["exp"])
        st.markdown('</div>', unsafe_allow_html=True)

        nm1_lines.append(
            f"NM1{p['surname']}/{p['names']} {p['title']}"
        )

        docs_lines.append(
            f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
            f"{p['country']}-{p['dob']}-{p['gender']}-"
            f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}-H/P{i}"
        )

    st.subheader("NM1 Entries")
    st.code("\n".join(nm1_lines))

    st.subheader("SRDOCS Entries")
    st.code("\n".join(docs_lines))
