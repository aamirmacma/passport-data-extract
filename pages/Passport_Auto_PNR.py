import streamlit as st
from passporteye import read_mrz
import datetime
import uuid
import os


# ================= SAFE DATE FUNCTIONS =================

def mrz_date_fix(d):

    # MRZ date missing ho to
    if d is None:
        return None

    d = str(d)

    if len(d) < 6:
        return None

    try:
        y = int(d[0:2])
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
        return "MSTR" if gender == "M" else "MISS"
    else:
        return "INF"


# ================= MAIN =================

def run():

    st.subheader("🛂 Passport Auto PNR")

    files = st.file_uploader(
        "Upload Passport Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    passengers = []
    seen = set()

    if not files:
        return

    for f in files:

        # ===== TEMP SAVE SAFE =====
        temp_file = f"temp_{uuid.uuid4().hex}.jpg"

        try:
            with open(temp_file, "wb") as fp:
                fp.write(f.read())
        except:
            st.error("File read error")
            continue

        # ===== MRZ READ =====
        try:
            mrz = read_mrz(temp_file)
        except:
            mrz = None

        if mrz is None:
            st.warning("MRZ not detected")
            os.remove(temp_file)
            continue

        data = mrz.to_dict()

        passport = data.get("number", "")

        if passport in seen:
            st.warning(f"Duplicate skipped: {passport}")
            os.remove(temp_file)
            continue

        seen.add(passport)

        surname = data.get("surname", "").replace("<", "")
        names = data.get("names", "").replace("<", " ")

        age, dob = calculate_age(data.get("date_of_birth"))
        exp = safe_date(data.get("expiration_date"))

        gender = data.get("sex", "M")
        country = data.get("country", "")

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

        os.remove(temp_file)

    # ================= OUTPUT =================

    if not passengers:
        return

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
