import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
from PIL import Image
import io

# ================= TESSERACT =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ================= PAGE =================
st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background:#f4f7fb; }

.header {
    background:linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:white;
    font-size:24px;
    font-weight:700;
}

.box {
    background:white;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #1c7ed6;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="header">✈️ Amadeus Auto PNR Builder <span style="font-size:14px;">Developed by Aamir Khan</span></div>',
    unsafe_allow_html=True
)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs([
    "🛂 Passport Auto PNR",
    "📸 Passport Photo Maker",
    "🖼 Passport Size Maker"
])

# =========================================================
# ================= COMMON FUNCTIONS ======================
# =========================================================

def mrz_date_fix(d):
    try:
        if not d or len(d) < 6:
            return None
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
    dt = mrz_date_fix(d)
    if not dt:
        return 0, ""
    today = datetime.datetime.today()
    age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
    return age, dt.strftime("%d%b%y").upper()


def passenger_title(age, gender):
    if age < 2:
        return "INF"
    elif age < 12:
        return "CHD"
    else:
        return "MR" if gender == "M" else "MRS"


def parse_mrz_names(surname, names):
    surname = surname.replace("<", "").strip().upper()
    names = names.replace("<", " ").upper()

    clean = []
    for w in names.split():
        if len(w) <= 1:
            continue
        if len(set(w)) == 1:   # remove KKKKK
            continue
        clean.append(w)

    return surname, " ".join(clean)


def fast_mrz_read(path):
    img = cv2.imread(path)
    if img is None:
        return None

    h, w = img.shape[:2]
    crop = img[int(h * 0.70):h, 0:w]

    temp = "mrz_temp.jpg"
    cv2.imwrite(temp, crop)

    try:
        mrz = read_mrz(temp)
    except:
        mrz = None

    os.remove(temp)
    return mrz


def extract_extra_fields(path):
    img = cv2.imread(path)
    if img is None:
        return "", "", "", ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)

    father, pob, doi, cnic = "", "", "", ""

    for line in text.upper().split("\n"):
        if "FATHER" in line or "HUSBAND" in line:
            father = line.replace("FATHER NAME", "").strip()

        if "PLACE OF BIRTH" in line:
            pob = line.replace("PLACE OF BIRTH", "").strip()

        if "DATE OF ISSUE" in line:
            doi = line.replace("DATE OF ISSUE", "").strip()

        m = re.search(r"\d{5}-\d{7}-\d", line)
        if m:
            cnic = m.group()

    return father, pob, doi, cnic


# =========================================================
# ================= TAB 1 : PASSPORT ======================
# =========================================================

with tab1:

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

            mrz = fast_mrz_read(temp)

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

            age, dob = calculate_age(d.get("date_of_birth"))
            exp = safe_date(d.get("expiration_date"))

            father, pob, doi, cnic = extract_extra_fields(temp)

            passengers.append({
                "surname": surname,
                "names": names,
                "passport": passport,
                "dob": dob,
                "exp": exp,
                "gender": d.get("sex", "M"),
                "country": d.get("country", "PAK"),
                "age": age,
                "father": father,
                "pob": pob,
                "doi": doi,
                "cnic": cnic
            })

            os.remove(temp)

    if passengers:

        nm1_lines = []
        docs_lines = []

        st.subheader("Extracted Passport Details")

        for i, p in enumerate(passengers, 1):
            st.markdown('<div class="box">', unsafe_allow_html=True)
            st.write(f"Passenger {i}: {p['surname']} {p['names']}")
            st.write("Passport:", p["passport"])
            st.write("DOB:", p["dob"])
            st.write("Expiry:", p["exp"])
            st.write("Father/Husband:", p["father"])
            st.write("Place of Birth:", p["pob"])
            st.write("CNIC:", p["cnic"])
            st.markdown("</div>", unsafe_allow_html=True)

            title = passenger_title(p["age"], p["gender"])

            nm1_lines.append(
                f"NM1{p['surname']}/{p['names']} {title}"
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


# =========================================================
# ================= TAB 2 : PHOTO MAKER ===================
# =========================================================

with tab2:

    photo = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"])

    if photo:
        img = Image.open(photo).convert("RGB")
        img = img.resize((300, 400))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)

        st.image(img)

        st.download_button(
            "Download Passport Photo",
            buf.getvalue(),
            file_name="passport_photo.jpg"
        )


# =========================================================
# ================= TAB 3 : SIZE MAKER ====================
# =========================================================

with tab3:

    st.info("JPG only — Max file size 500KB")

    photo = st.file_uploader("Upload JPG Photo", type=["jpg"])

    if photo:

        img = Image.open(photo).convert("RGB")
        img = img.resize((413, 531))  # passport size ratio

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)

        size_kb = len(buf.getvalue()) / 1024

        st.image(img)
        st.write(f"Final Size: {round(size_kb,2)} KB")

        st.download_button(
            "Download Passport Size Photo",
            buf.getvalue(),
            file_name="passport_size.jpg"
        )
