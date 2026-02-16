import streamlit as st
from passporteye import read_mrz
import datetime
import uuid
import os

# ================= DATE FUNCTIONS =================

def mrz_date_fix(d):
    if not d or len(d) != 6:
        return None

    y = int(d[:2])
    m = int(d[2:4])
    da = int(d[4:6])

    if y > datetime.datetime.now().year % 100:
        y += 1900
    else:
        y += 2000

    return datetime.datetime(y, m, da)

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
        return "MSTR" if gender == "M" else "MISS"
    else:
        return "INF"

# ================= MAIN RUN =================

def run():

    st.subheader("🛂 Passport Auto PNR")

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

            try:
                mrz = read_mrz(temp)
            except:
                mrz = None

            if mrz:

                d = mrz.to_dict()
                passport = d.get("number", "")

                if passport in seen:
                    st.warning(f"Duplicate skipped: {passport}")
                    os.remove(temp)
                    continue

                seen.add(passport)

                surname = d.get("surname", "").replace("<", "")
                names = d.get("names", "").replace("<", " ")

                age, dob = calculate_age(d.get("date_of_birth"))
                exp = safe_date(d.get("expiration_date"))

                gender = d.get("sex", "M")
                country = d.get("country", "")

                passengers.append({
                    "surname": surname,
                    "names": names,
                    "passport": passport,
                    "dob": dob,
                    "exp": exp,
                    "gender": gender,
                    "country": country,
                    "age": age
                })

            else:
                st.warning("MRZ not detected")

            os.remove(temp)

    # ================= OUTPUT =================

    if passengers:

        st.subheader("Extracted Passport Details")

        nm1_lines = []
        docs_lines = []

        for i, p in enumerate(passengers, 1):

            title = passenger_title(p["age"], p["gender"])

            st.write(f"Passenger {i}: {p['surname']} {p['names']}")
            st.write("Passport:", p["passport"])
            st.write("DOB:", p["dob"])
            st.write("Expiry:", p["exp"])
            st.divider()

            nm1_lines.append(
                f"NM1{p['surname']}/{p['names']} {title}"
            )

            docs_lines.append(
                f"SRDOCS HK1-P-{p['country']}-{p['passport']}-"
                f"{p['country']}-{p['dob']}-{p['gender']}-"
                f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}"
            )

        st.subheader("NM1 Entries")
        st.code("\n".join(nm1_lines))

        st.subheader("SRDOCS Entries")
        st.code("\n".join(docs_lines))
