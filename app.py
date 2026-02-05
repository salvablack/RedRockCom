import time
import base64
import hashlib
from nacl.secret import SecretBox
from nacl.utils import random as nacl_random
from nacl.pwhash import argon2id
import streamlit as st

st.set_page_config(page_title="Chat E2EE por Room ID", layout="centered")

# ---------------------------------------------------
# "Base de datos" en memoria (demo)
# En producción esto sería Redis / DB
# ---------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = {}

# ---------------------------------------------------
# DERIVACIÓN DE CLAVE DESDE ROOM ID (Argon2)
# ---------------------------------------------------

def derive_key(room_id: str) -> bytes:
    salt = hashlib.sha256(room_id.encode()).digest()
    key = argon2id.kdf(
        SecretBox.KEY_SIZE,
        room_id.encode(),
        salt,
        opslimit=argon2id.OPSLIMIT_MODERATE,
        memlimit=argon2id.MEMLIMIT_MODERATE,
    )
    return key


def encrypt_message(box: SecretBox, message: str) -> str:
    nonce = nacl_random(SecretBox.NONCE_SIZE)
    encrypted = box.encrypt(message.encode(), nonce)
    return base64.b64encode(encrypted).decode()


def decrypt_message(box: SecretBox, ciphertext: str) -> str:
    try:
        raw = base64.b64decode(ciphertext.encode())
        decrypted = box.decrypt(raw)
        return decrypted.decode()
    except Exception:
        return "[Mensaje ilegible]"


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🔐 Chat cifrado extremo a extremo por Room ID")

room_id = st.text_input("Room ID (clave secreta compartida)", type="password")

if not room_id:
    st.stop()

key = derive_key(room_id)
box = SecretBox(key)

# Inicializar sala
if room_id not in st.session_state.messages:
    st.session_state.messages[room_id] = []

# ---------------------------------------------------
# MOSTRAR MENSAJES DESCIFRADOS
# ---------------------------------------------------

st.subheader("Mensajes")

for ciphertext, timestamp in st.session_state.messages[room_id]:
    msg = decrypt_message(box, ciphertext)
    st.write(f"🕒 {timestamp} — {msg}")

# ---------------------------------------------------
# ENVIAR MENSAJE
# ---------------------------------------------------

st.divider()
msg_input = st.text_input("Escribe un mensaje")

if st.button("Enviar") and msg_input:
    encrypted = encrypt_message(box, msg_input)
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.messages[room_id].append((encrypted, timestamp))
    st.rerun()
