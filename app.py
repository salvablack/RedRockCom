import base64
import hashlib
import time

import streamlit as st
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

st.set_page_config(page_title="Chat E2EE por Room ID", layout="centered")

# ---------------------------------------------------
# "Base de datos" temporal
# ---------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = {}

# ---------------------------------------------------
# DERIVAR CLAVE FUERTE DESDE ROOM ID
# ---------------------------------------------------

def derive_key(room_id: str) -> bytes:
    salt = hashlib.sha256(room_id.encode()).digest()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(room_id.encode()))
    return key


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🔐 Chat cifrado extremo a extremo por Room ID")

room_id = st.text_input("Room ID (clave secreta compartida)", type="password")

if not room_id:
    st.stop()

fernet = Fernet(derive_key(room_id))

# Inicializar sala
if room_id not in st.session_state.messages:
    st.session_state.messages[room_id] = []

# ---------------------------------------------------
# MOSTRAR MENSAJES
# ---------------------------------------------------

st.subheader("Mensajes")

for ciphertext, timestamp in st.session_state.messages[room_id]:
    try:
        msg = fernet.decrypt(ciphertext.encode()).decode()
    except Exception:
        msg = "[Mensaje ilegible]"
    st.write(f"🕒 {timestamp} — {msg}")

# ---------------------------------------------------
# ENVIAR MENSAJE
# ---------------------------------------------------

st.divider()
msg_input = st.text_input("Escribe un mensaje")

if st.button("Enviar") and msg_input:
    encrypted = fernet.encrypt(msg_input.encode()).decode()
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.messages[room_id].append((encrypted, timestamp))
    st.rerun()
