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


# ================= FUNCTIONS =================

def mrz_date_fix(d):

    if not d:
        return None

    d = str(d)

    if len(d) < 6:
        return None

    try:
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
    if not dt:
        return ""
    return dt.strftime("%d%b%y").upper()


def calculate_age(d):

    birth = mrz_date_fix(d)

    if not birth:
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

        # remove garbage names
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


# ================= MAIN RUN =================

def run():

    st.subheader("Passport Auto PNR")

    files = st.file_uploader(
        "Upload Passport Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if not files:
        return

    passengers = []
    seen = set()

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

    if not passengers:
        return

    nm1_lines = []
    docs_lines = []

    st.subheader("Extracted Passport Details")

    for i, p in enumerate(passengers, 1):

        st.write(f"Passenger {i}: {p['surname']} {p['names']}")
        st.write("Passport:", p["passport"])
        st.write("DOB:", p["dob"])
        st.write("Expiry:", p["exp"])
        st.write("---")

    pax = 1

    for p in passengers:

        nm1_lines.append(
            f"NM1{p['surname']}/{p['names']} {p['title']}"
        )

        docs_lines.append(
            f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
            f"{p['country']}-{p['dob']}-{p['gender']}-"
            f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}-H/P{pax}"
        )

        pax += 1

    export_text = "\n".join(nm1_lines) + "\n\n" + "\n".join(docs_lines)

    st.code(export_text)

    st.download_button(
        "Download Amadeus PNR",
        export_text,
        "amadeus_pnr.txt"
    )
