import base64
import hashlib
import time
import pandas as pd
import streamlit as st
import gspread
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Chat E2EE", layout="centered")

# ---------------------------------------------------
# GOOGLE SHEETS CONEXIÓN
# ---------------------------------------------------

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)

SHEET_ID = "PEGA_AQUI_EL_ID_DEL_SHEET"
sheet = client.open_by_key(SHEET_ID).sheet1

# ---------------------------------------------------
# CRIPTO
# ---------------------------------------------------

def derive_key(room_id: str) -> bytes:
    salt = hashlib.sha256(room_id.encode()).digest()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(room_id.encode()))

# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🔐 Chat E2EE por Room ID")

room_id = st.text_input("Room ID", type="password")
if not room_id:
    st.stop()

fernet = Fernet(derive_key(room_id))

# ---------------------------------------------------
# LEER MENSAJES DEL SHEET
# ---------------------------------------------------

data = sheet.get_all_records()
df = pd.DataFrame(data)

room_msgs = df[df["room"] == room_id]

st.subheader("Mensajes")

for _, row in room_msgs.iterrows():
    try:
        msg = fernet.decrypt(row["msg"].encode()).decode()
        st.write(f"🕒 {row['time']} — {msg}")
    except:
        pass

# ---------------------------------------------------
# ENVIAR MENSAJE
# ---------------------------------------------------

msg = st.text_input("Escribe mensaje")

if st.button("Enviar") and msg:
    encrypted = fernet.encrypt(msg.encode()).decode()
    sheet.append_row([room_id, encrypted, time.strftime("%H:%M:%S")])
    st.rerun()
