import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(page_title="Solo Escuchar al Otro", layout="wide")

st.title("🎙️ Solo Escuchar al Otro (Sin Eco de Mi Voz)")

st.warning("""
**Objetivo:** Tus auriculares deben reproducir **solo la voz de la otra persona**.  
No debes escuchar tu propia voz.
""")

st.markdown("### 🔑 Instrucciones obligatorias:")
st.markdown("1. **Usa auriculares** (imprescindible para que funcione bien)")
st.markdown("2. Permite acceso al micrófono")
st.markdown("3. Abre la app en **dos dispositivos/pestañas** con el mismo Room ID")
st.markdown("4. Habla en una → solo deberías escuchar al otro en tus auriculares")

# Configuración ICE (STUN + TURN recomendados)
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {
            "urls": ["turn:openrelay.metered.ca:80", "turn:openrelay.metered.ca:443?transport=tcp"],
            "username": "openrelayproject",
            "credential": "openrelayproject"
        },
        {
            "urls": "turn:numb.viagenie.ca",
            "username": "webrtc@live.com",
            "credential": "muazkh"
        }
    ]
)

# Room ID
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room = st.text_input("Room ID (compártelo exactamente)", value=st.session_state.room_id)

if st.button("Unirse / Cambiar sala"):
    st.session_state.room_id = room.strip() or st.session_state.room_id
    st.rerun()

st.markdown(f"**Room ID actual:** `{st.session_state.room_id}`")

# Constraints agresivas para eliminar eco local
audio_constraints = {
    "mandatory": {
        "echoCancellation": True,
        "echoCancellationType": "system",        # "system" suele ser mejor que "browser"
        "noiseSuppression": True,
        "autoGainControl": True,
        "googEchoCancellation": True,
        "googAutoGainControl": True,
        "googNoiseSuppression": True,
        "googHighpassFilter": True,
        "googTypingNoiseDetection": True
    },
    "optional": []
}

ctx = webrtc_streamer(
    key=f"only_remote_audio_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,
    audio_html_attrs={
        "controls": True,
        "style": {"width": "100%", "margin": "20px 0"}
    }
)

# Diagnóstico
col1, col2 = st.columns(2)

with col1:
    if ctx.input_audio_track:
        st.success("✅ Enviando tu voz al otro")
    else:
        st.error("❌ Micrófono no detectado")

with col2:
    if ctx.state.playing:
        st.success("🟢 Reproduciendo audio del otro → Deberías escuchar SOLO al otro")
    else:
        st.warning("🔴 No reproduciendo audio recibido todavía")

st.markdown("---")
st.markdown("### ¿Qué esperar con auriculares?")
st.markdown("- Tus auriculares **solo deben reproducir la voz de la otra persona**")
st.markdown("- No debes escuchar tu propia voz (el echo cancellation + auriculares lo evitan)")
st.markdown("- Si aún escuchas tu voz → baja el volumen general de la computadora o prueba otros auriculares")

st.caption("Si después de usar auriculares sigues escuchando tu propia voz fuerte, copia los errores de la consola del navegador (F12 → Console) y pégamelos aquí.")
