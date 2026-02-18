import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re

# ================= TESSERACT =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ==================================================
# MAIN FUNCTION
# ==================================================
def run():

    st.header("✈️ Passport Auto PNR Builder")

    # ---------- DATE FIX ----------
    def mrz_date_fix(d):
        try:
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


    # ---------- AGE CALCULATION (Y M D) ----------
    def calculate_age_full(d):
        birth = mrz_date_fix(d)
        today = datetime.datetime.today()

        years = today.year - birth.year
        months = today.month - birth.month
        days = today.day - birth.day

        if days < 0:
            months -= 1
            days += 30

        if months < 0:
            years -= 1
            months += 12

        return years, months, days


    # ---------- TITLE ----------
    def passenger_title(age_y, gender):

        if age_y < 2:
            return "INF"

        elif age_y < 12:
            return "MSTR" if gender == "M" else "MISS"

        else:
            if gender == "M":
                return "MR"
            else:
                return "MRS"


    # ---------- NAME CLEANER ----------
    def clean_word(w):
        if len(w) <= 1:
            return False
        if len(set(w)) == 1:
            return False
        if w.count("K") > len(w) * 0.6:
            return False
        return True


    def split_joined_name(name):
        patterns = [
            "ABDUR", "ABDUL", "REHMAN", "RAHMAN",
            "SYED", "AHMED", "MUHAMMAD", "MOHAMMAD",
            "ALI", "HUSSAIN", "HASSAN", "KHAN"
        ]

        for p in patterns:
            name = name.replace(p, " " + p)

        return " ".join(name.split())


    def parse_mrz_names(surname, names):

        surname = surname.replace("<", "").strip().upper()
        names = names.replace("<", " ")
        names = " ".join(names.split()).upper()

        words = []
        for w in names.split():
            if clean_word(w):
                words.append(split_joined_name(w))

        return surname, " ".join(words)


    # ---------- OCR EXTRA ----------
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

            if "FATHER" in line or "HUSBAND" in line:
                if i + 1 < len(lines):
                    father = lines[i+1].strip()

            m = re.search(r"\d{5}-\d{7}-\d", line)
            if m:
                cnic = m.group()

        return father, cnic


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

    if files:

        for f in files:

            temp = f"temp_{uuid.uuid4().hex}.jpg"

            with open(temp, "wb") as fp:
                fp.write(f.getbuffer())

            auto_rotate(temp)

            mrz = read_mrz(temp)
            if not mrz:
                os.remove(temp)
                continue

            d = mrz.to_dict()

            surname, names = parse_mrz_names(
                d.get("surname", ""),
                d.get("names", "")
            )

            gender = d.get("sex", "M")

            age_y, age_m, age_d = calculate_age_full(
                d.get("date_of_birth")
            )

            title = passenger_title(age_y, gender)

            passengers.append({
                "surname": surname,
                "names": names,
                "title": title,
                "dob": safe_date(d.get("date_of_birth")),
                "exp": safe_date(d.get("expiration_date")),
                "age_y": age_y,
                "age_m": age_m,
                "age_d": age_d,
                "passport": d.get("number"),
                "country": d.get("country"),
                "gender": gender
            })

            os.remove(temp)


    # ================= OUTPUT =================
    if passengers:

        st.subheader("Extracted Passport Details")

        adults, children, infants = [], [], []

        for p in passengers:

            st.write(
                f"{p['surname']} {p['names']} | "
                f"Age: {p['age_y']}Y {p['age_m']}M {p['age_d']}D"
            )

            if p["title"] == "INF":
                infants.append(p)
            elif p["title"] in ["MSTR","MISS"]:
                children.append(p)
            else:
                adults.append(p)

        # ---------- NM1 ----------
        nm1_lines = []
        inf_index = 0

        for adult in adults:

            nm1 = f"NM1{adult['surname']}/{adult['names']} {adult['title']}"

            if inf_index < len(infants):
                inf = infants[inf_index]
                nm1 += f" (INF/{inf['surname']} {inf['names']}/{inf['dob']})"
                inf_index += 1

            nm1_lines.append(nm1)

        for chd in children:
            nm1_lines.append(
                f"NM1{chd['surname']}/{chd['names']} "
                f"{chd['title']} (CHD/{chd['dob']})"
            )

        st.subheader("NM1 Entries")
        st.code("\n".join(nm1_lines))
