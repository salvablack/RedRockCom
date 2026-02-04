import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(page_title="Sala de Audio Privada - Solo Voz", layout="wide")

st.title("🎙️ Sala de Audio Privada (Solo Voz - Máximo 3 personas)")

st.markdown("""
### Instrucciones importantes para evitar eco y mejorar la experiencia:
1. **Usa auriculares** (la solución más efectiva contra el eco fuerte de tu propia voz)  
2. Si no tienes auriculares, **baja mucho el volumen** de los altavoces de tu computadora  
3. Permite el acceso al **micrófono** cuando el navegador lo solicite  
4. Prueba primero con **dos pestañas o dos dispositivos** usando el **mismo Room ID**  
5. Habla en una pestaña y escucha en la otra para verificar que el audio remoto llega
""")

# ── Configuración ICE Servers (STUN + varios TURN públicos) ──
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
        {
            "urls": ["turn:openrelay.metered.ca:80", "turn:openrelay.metered.ca:443?transport=tcp"],
            "username": "openrelayproject",
            "credential": "openrelayproject"
        },
        {
            "urls": "turn:numb.viagenie.ca",
            "username": "webrtc@live.com",
            "credential": "muazkh"
        },
        {
            "urls": "turn:turn.anyfirewall.com:443?transport=tcp",
            "username": "webrtc",
            "credential": "webrtc"
        }
    ]
)

# ── Gestión del Room ID ──
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room_input = st.text_input(
    "Room ID (compártelo exactamente igual con los demás)",
    value=st.session_state.room_id,
    help="Usa el mismo ID en todos los dispositivos que quieran conectarse"
)

if st.button("Unirse / Cambiar sala"):
    new_room = room_input.strip()
    if new_room and new_room != st.session_state.room_id:
        st.session_state.room_id = new_room
        st.success(f"¡Sala cambiada a: **{st.session_state.room_id}**!")
        st.rerun()

st.markdown(f"**Room ID actual para compartir:**  `{st.session_state.room_id}`")

# ── Configuración avanzada de audio para reducir eco ──
audio_constraints = {
    "mandatory": {
        "echoCancellation": True,
        "noiseSuppression": True,
        "autoGainControl": True
    },
    "optional": [
        {"echoCancellationType": "system"},  # Mejor en la mayoría de casos
        {"googEchoCancellation": True},
        {"googAutoGainControl": True},
        {"googNoiseSuppression": True},
        {"googHighpassFilter": True},
        {"googTypingNoiseDetection": True}
    ]
}

# ── Componente WebRTC ── solo audio ──
ctx = webrtc_streamer(
    key=f"audio_private_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,           # Inicia automáticamente
    video_html_attrs=None,                # No mostramos video
    audio_html_attrs={
        "controls": True,
        "style": {"width": "100%", "margin": "10px 0"}
    }
)

# ── Estado y mensajes de diagnóstico ──
col1, col2 = st.columns([3, 2])

with col1:
    if ctx.input_audio_track:
        st.success("✅ Micrófono detectado y activo")
        st.info("Habla ahora... el audio debería llegar a los demás participantes")
    else:
        st.warning("⚠️ No se detecta micrófono activo")
        st.markdown("""
        Posibles soluciones:
        - Verifica que diste permiso al micrófono
        - Prueba en **Chrome** o **Edge** (más estables)
        - Conecta/desconecta auriculares o micrófono externo
        """)

with col2:
    st.markdown("### Estado de conexión")
    if ctx.state.playing:
        st.success("🟢 Reproduciendo audio")
    else:
        st.error("🔴 No está reproduciendo")

    st.markdown("**Consejo rápido anti-eco:**")
    st.markdown("- Auriculares → casi siempre soluciona")
    st.markdown("- Volumen bajo en altavoces")
    st.markdown("- Distancia mic ↔ altavoz")

st.markdown("---")
st.caption("""
Versión optimizada para reducir eco al máximo.  
Si aún escuchas tu voz muy fuerte: **prueba obligatoriamente con auriculares**.  
Si no escuchas al otro participante: copia los errores de la consola del navegador (F12 → Console) y compártelos.
""")
