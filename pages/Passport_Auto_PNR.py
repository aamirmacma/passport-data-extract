import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import streamlit.components.v1 as components


# ================= TESSERACT AUTO =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ================= HEADER =================
st.markdown("""
<style>
.stApp { background-color:#f4f7fb; }

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
</style>

<div class="header-bar">
    <div class="header-title">✈️ Passport Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)


# ================= FUNCTIONS =================

def mrz_date_fix(d):

    if not d:
        return None

    try:
        d = str(d)
        if len(d) < 6:
            return None

        y = int(d[:2])
        m = int(d[2:4])
        da = int(d[4:6])

        current_year = datetime.datetime.now().year % 100

        if y > current_year:
            y += 1900
        else:
            y += 2000

        return datetime.datetime(y, m, da)

    except:
        return None


def safe_date(d):
    dt = mrz_date_fix(d)
    if dt is None:
        return ""
    return dt.strftime("%d%b%y").upper()


def calculate_age(d):

    birth = mrz_date_fix(d)

    if birth is None:
        return 0, ""

    today = datetime.datetime.today()

    age = today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

    return age, birth.strftime("%d%b%y").upper()


def passenger_title(age, gender):
    if age >= 12:
        return "MR" if gender == "M" else "MRS"
    elif age >= 2:
        return "CHD"
    else:
        return "INF"


def parse_mrz_names(surname, names):

    surname = surname.replace("<", "").strip().upper()
    names = names.replace("<", " ")
    names = " ".join(names.split())

    clean = []
    for w in names.split():
        if len(w) <= 1:
            continue
        if len(set(w)) == 1:
            continue
        if w.count("K") > len(w) * 0.6:
            continue
        clean.append(w)

    return surname, " ".join(clean)


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

        gender = d.get("sex", "M")
        country = d.get("country", "")

        age, dob = calculate_age(d.get("date_of_birth"))
        exp = safe_date(d.get("expiration_date"))
        title = passenger_title(age, gender)

        passengers.append({
            "surname": surname,
            "names": names,
            "title": title,
            "passport": passport,
            "dob": dob,
            "exp": exp,
            "gender": gender,
            "country": country
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
        st.write("Surname:", p["surname"])
        st.write("Given Name:", p["names"])
        st.write("Title:", p["title"])
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

    export_text = "\n".join(nm1_lines) + "\n\n" + "\n".join(docs_lines)

    st.subheader("NM1 Entries")
    st.code("\n".join(nm1_lines))

    st.subheader("SRDOCS Entries")
    st.code("\n".join(docs_lines))

    st.download_button(
        "⬇ Download Amadeus PNR (TXT)",
        data=export_text,
        file_name="amadeus_pnr.txt",
        mime="text/plain"
    )

    components.html(f"""
    <button style="background:#1c7ed6;color:white;
    padding:10px 18px;border:none;border-radius:6px;
    font-size:16px;cursor:pointer;"
    onclick="navigator.clipboard.writeText(`{export_text}`)">
    📋 Copy PNR to Clipboard
    </button>
    """, height=60)
