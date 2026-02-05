import base64
import hashlib
import time
import requests
import streamlit as st
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

SERVER = "https://TU_APP.streamlit.app"  # misma app

st.set_page_config(page_title="Chat E2EE", layout="centered")


def derive_key(room_id: str) -> bytes:
    salt = hashlib.sha256(room_id.encode()).digest()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(room_id.encode()))


st.title("🔐 Chat E2EE por Room ID")

room_id = st.text_input("Room ID", type="password")
if not room_id:
    st.stop()

fernet = Fernet(derive_key(room_id))

# ---------------------------------------------------
# Leer mensajes del servidor
# ---------------------------------------------------

resp = requests.get(f"{SERVER}/messages/{room_id}")
ciphertexts = resp.json()

st.subheader("Mensajes")

for c in ciphertexts:
    try:
        st.write(fernet.decrypt(c.encode()).decode())
    except:
        pass

# ---------------------------------------------------
# Enviar mensaje
# ---------------------------------------------------

msg = st.text_input("Mensaje")

if st.button("Enviar") and msg:
    encrypted = fernet.encrypt(msg.encode()).decode()
    requests.post(f"{SERVER}/send", json={"room": room_id, "msg": encrypted})
    st.rerun()
