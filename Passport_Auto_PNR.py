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


    # ---------- AGE CALCULATION ----------
    def calculate_age_full(dob):

        birth = mrz_date_fix(dob)
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


    # ---------- UPLOAD ----------
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

            mrz = read_mrz(temp)

            if not mrz:
                os.remove(temp)
                continue

            d = mrz.to_dict()

            surname = d["surname"].replace("<", "")
            names = d["names"].replace("<", " ")
            passport = d["number"]

            gender = d["sex"]
            country = d["country"]

            age_y, age_m, age_d = calculate_age_full(
                d["date_of_birth"]
            )

            dob = safe_date(d["date_of_birth"])
            exp = safe_date(d["expiration_date"])

            title = passenger_title(age_y, gender)

            passengers.append({
                "surname": surname,
                "names": names,
                "passport": passport,
                "gender": gender,
                "country": country,
                "dob": dob,
                "exp": exp,
                "title": title,
                "age_y": age_y,
                "age_m": age_m,
                "age_d": age_d
            })

            os.remove(temp)


    # ================= OUTPUT =================
    if passengers:

        st.subheader("Passenger Details")

        adults, children, infants = [], [], []

        for p in passengers:

            st.write(
                f"{p['surname']} {p['names']} — "
                f"Age: {p['age_y']}Y {p['age_m']}M {p['age_d']}D"
            )

            if p["title"] == "INF":
                infants.append(p)
            elif p["title"] in ["MSTR", "MISS"]:
                children.append(p)
            else:
                adults.append(p)

        # ---------- NM1 ----------
        st.subheader("NM1 Entries")

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
                f"NM1{chd['surname']}/{chd['names']} {chd['title']} (CHD/{chd['dob']})"
            )

        st.code("\n".join(nm1_lines))


        # ---------- SRDOCS ----------
        st.subheader("SRDOCS Entries")

        docs_lines = []
        pax = 1

        for p in passengers:

            docs_lines.append(
                f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
                f"{p['country']}-{p['dob']}-{p['gender']}-"
                f"{p['exp']}-{p['surname']}-"
                f"{p['names'].replace(' ','-')}-H/P{pax}"
            )

            pax += 1

        st.code("\n".join(docs_lines))
