import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(page_title="Sala de Audio Privada - Solo Voz (Anti-Eco)", layout="wide")

st.title("🎙️ Sala de Audio Privada (Solo Voz - Máximo 3 personas)")

st.warning("""
**Problema actual detectado:** Escuchas tu voz fuerte (eco/local playback) pero el audio del otro llega mal o no llega.  
Solución principal → **usa auriculares**. Si no puedes, baja al máximo el volumen de tus altavoces mientras pruebas.
""")

st.markdown("### Instrucciones rápidas")
st.markdown("1. Usa **auriculares** (la diferencia es inmediata)")
st.markdown("2. Permite micrófono")
st.markdown("3. Abre **dos pestañas/dispositivos** con el **mismo Room ID**")
st.markdown("4. Habla en una → escucha en la otra")

# ── TURN/STUN más robusto ──
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

# ── Room ID ──
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room = st.text_input("Room ID (compártelo exactamente)", value=st.session_state.room_id)

if st.button("Unirse / Refrescar"):
    st.session_state.room_id = room.strip() or st.session_state.room_id
    st.rerun()

st.markdown(f"**Room ID para compartir:** `{st.session_state.room_id}`")

# ── Constraints muy agresivas para echo cancellation ──
audio_constraints = {
    "mandatory": {
        "echoCancellation": True,
        "echoCancellationType": "system",  # Prueba "browser" si no funciona
        "noiseSuppression": True,
        "autoGainControl": True
    },
    "optional": [
        {"googEchoCancellation": True},
        {"googAutoGainControl": True},
        {"googNoiseSuppression": True},
        {"googHighpassFilter": True}
    ]
}

ctx = webrtc_streamer(
    key=f"audio_antiec_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,
    audio_html_attrs={
        "controls": True,
        "style": {"width": "100%", "margin": "15px 0"}
    }
)

# ── Diagnóstico claro ──
if ctx.input_audio_track:
    st.success("✅ Tu micrófono está enviando audio (el otro debería escucharte)")
else:
    st.error("❌ No detecta micrófono → verifica permisos o prueba otro navegador")

if ctx.state.playing:
    st.success("🟢 Reproduciendo audio recibido → deberías escuchar al otro aquí")
    st.info("Si no escuchas nada del otro → prueba auriculares + volumen bajo + otro navegador")
else:
    st.warning("🔴 No está reproduciendo audio recibido todavía")

st.markdown("""
### ¿Qué hacer si sigues sin escuchar al otro?
- Confirma que el otro también tiene micrófono activo (pídele que hable fuerte o ponga música cerca del mic)
- Abre la consola del navegador (F12 → Console) y busca errores con "ICE", "audio", "echo" o "failed"
- Prueba en **Chrome** (mejor soporte WebRTC) o **Edge**
- Cambia de red (WiFi → datos móviles)
- Dime qué ves exactamente: ¿el otro te escucha a ti? ¿tú escuchas algo (aunque sea bajo)?
""")

st.caption("Nota: En laptops sin auriculares el echo cancellation del navegador lucha mucho. Auriculares resuelven casi siempre.")
