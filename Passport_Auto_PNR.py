import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re


# ================= TESSERACT PATH =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ==================================================
# MAIN RUN FUNCTION
# ==================================================
def run():

    st.title("✈️ Passport Auto PNR Builder")

    # ==================================================
    # FUNCTIONS
    # ==================================================

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
        if dt is None:
            return ""
        return dt.strftime("%d%b%y").upper()


    def calculate_age(d):
        birth = mrz_date_fix(d)

        if birth is None:
            return 30, ""

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


    # ---------- NAME CLEANER ----------
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


    # ---------- OCR EXTRACTION ----------
    def extract_extra_fields(path):

        img = cv2.imread(path)
        if img is None:
            return "", ""

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray).upper()

        father = ""
        cnic = ""

        lines = text.split("\n")

        for i, line in enumerate(lines):

            # Father / Husband detection
            if "FATHER" in line or "HUSBAND" in line:

                same_line = line.replace("FATHER NAME", "") \
                                .replace("HUSBAND NAME", "") \
                                .strip()

                if len(same_line) > 3:
                    father = same_line
                elif i + 1 < len(lines):
                    father = lines[i + 1].strip()

            # CNIC format 1
            m = re.search(r"\d{5}-\d{7}-\d", line)
            if m:
                cnic = m.group()

            # CNIC format 2
            m2 = re.search(r"\d{13}", line)
            if m2 and cnic == "":
                cnic = m2.group()

        return father, cnic


    def auto_rotate(path):
        img = cv2.imread(path)
        if img is None:
            return
        h, w = img.shape[:2]
        if h > w:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(path, img)


    # ==================================================
    # UPLOAD
    # ==================================================

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
            country = d.get("country", "PAK")

            age, dob = calculate_age(d.get("date_of_birth"))
            exp = safe_date(d.get("expiration_date"))

            father, cnic = extract_extra_fields(temp)
            title = passenger_title(age, gender)

            passengers.append({
                "surname": surname,
                "names": names,
                "title": title,
                "passport": passport,
                "dob": dob,
                "exp": exp,
                "gender": gender,
                "country": country,
                "father": father,
                "cnic": cnic
            })

            os.remove(temp)

    # ==================================================
    # OUTPUT
    # ==================================================

    if passengers:

        st.subheader("Extracted Passport Details")

        nm1_lines = []
        docs_lines = []

        pax = 1

        for i, p in enumerate(passengers, 1):

            st.markdown("---")

            st.markdown(f"""
**Passenger {i}**

Surname: {p['surname']}  
Given Name: {p['names']}  
Passport: {p['passport']}  
DOB: {p['dob']}  
Expiry: {p['exp']}  
Gender: {p['gender']}  
Father/Husband: {p['father']}  
CNIC: {p['cnic']}
""")

            nm1_lines.append(
                f"NM1{p['surname']}/{p['names']} {p['title']}"
            )

            docs_lines.append(
                f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
                f"{p['country']}-{p['dob']}-{p['gender']}-"
                f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}/P{pax}"
            )

            pax += 1

        st.subheader("NM1 Entries")
        st.code("\n".join(nm1_lines))

        st.subheader("SRDOCS Entries")
        st.code("\n".join(docs_lines))
