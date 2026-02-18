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


    # ---------- AGE FULL ----------
    def calculate_age_full(dob_str):

        birth = mrz_date_fix(dob_str)
        if birth is None:
            return 0, 0, 0

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
    def passenger_title(age_years, gender):

        if age_years < 2:
            return "INF"
        elif age_years < 12:
            return "MSTR" if gender == "M" else "MISS"
        else:
            return "MR" if gender == "M" else "MRS"


    # ---------- NAME CLEAN ----------
    def clean_word(w):
        if len(w) <= 1:
            return False
        if len(set(w)) == 1:
            return False
        return True


    def parse_mrz_names(surname, names):

        surname = surname.replace("<", "").strip().upper()
        names = names.replace("<", " ")
        names = " ".join(names.split()).upper()

        return surname, names


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


    # ================= TRAVEL DETAILS =================
    st.subheader("Travel Details")

    col1, col2 = st.columns(2)

    with col1:
        departure_date = st.date_input("Departure Date")

    with col2:
        return_date = st.date_input("Return Date")

    if departure_date and return_date:
        total_days = (return_date - departure_date).days
        st.success(f"Total Stay: {total_days} Days")


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

            mrz = read_mrz(temp)

            if not mrz:
                st.warning("MRZ not detected")
                os.remove(temp)
                continue

            d = mrz.to_dict()
            passport = d.get("number", "")

            if passport in seen:
                os.remove(temp)
                continue

            seen.add(passport)

            surname, names = parse_mrz_names(
                d.get("surname", ""),
                d.get("names", "")
            )

            gender = d.get("sex", "M")
            country = d.get("country", "PAK")

            age_y, age_m, age_d = calculate_age_full(
                d.get("date_of_birth")
            )

            dob = safe_date(d.get("date_of_birth"))
            exp = safe_date(d.get("expiration_date"))

            father, cnic = extract_extra_fields(temp)
            title = passenger_title(age_y, gender)

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
                "cnic": cnic,
                "age_y": age_y,
                "age_m": age_m,
                "age_d": age_d
            })

            os.remove(temp)


    # ================= OUTPUT =================
    if passengers:

        st.subheader("Extracted Passport Details")

        nm1_lines = []
        docs_lines = []

        adults, children, infants = [], [], []

        for p in passengers:

            st.markdown(f"""
            **{p['surname']} {p['names']}**

            Passport: {p['passport']}  
            DOB: {p['dob']}  
            Age: {p['age_y']}Y {p['age_m']}M {p['age_d']}D  
            Gender: {p['gender']}  
            Father/Husband: {p['father']}  
            CNIC: {p['cnic']}
            """)

            if p["title"] == "INF":
                infants.append(p)
            elif p["title"] in ["MSTR", "MISS"]:
                children.append(p)
            else:
                adults.append(p)

        # ---------- NM1 ----------
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
                f"NM1{chd['surname']}/{chd['names']} {chd['title']} (CHD/{chd['dob']})"
            )

        st.subheader("NM1 Entries")
        st.code("\n".join(nm1_lines))

        # ---------- SRDOCS ----------
        pax = 1
        for p in passengers:

            docs_lines.append(
                f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
                f"{p['country']}-{p['dob']}-{p['gender']}-"
                f"{p['exp']}-{p['surname']}-"
                f"{p['names'].replace(' ','-')}-H/P{pax}"
            )

            pax += 1

        st.subheader("SRDOCS Entries")
        st.code("\n".join(docs_lines))

        # ---------- PNR COMMANDS ----------
        st.subheader("PNR Commands")

        dep = departure_date.strftime("%d%b").upper() if departure_date else "12APR"
        ret = return_date.strftime("%d%b").upper() if return_date else "26APR"

        pnr_commands = [
            f"AN{dep}KHIJED/ASV",
            "SS1T3",
            f"AN{ret}JEDKHI/ASV",
            "SS1T3",
            "AP",
            "TKOK",
            "ER",
            "IR"
        ]

        st.code("\n".join(pnr_commands))
