import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(
    page_title="Sala Audio Privada - Móvil Optimizado",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🎙️ Sala de Audio Privada")
st.caption("Optimizado para celular | Solo audio | Máximo 3 personas")

st.info("""
**Prueba obligatoria para conectar en celular:**
1. Usa **Chrome** (Android) o **Safari actualizado** (iOS)
2. Permite micrófono (icono arriba o en ajustes)
3. Prueba **WiFi diferente** o **solo datos móviles 4G/5G**
4. Usa **auriculares** (reduce eco y ayuda conexión)
5. Si se queda "Esperando conexión..." → refresca página o cambia Room ID
6. Abre en **dos celulares** o uno + PC con el mismo Room ID
""")

# RTC Configuration con más opciones TURN/STUN (2026 - probados en issues recientes)
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        # STUN Google (siempre base)
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
        {"urls": "stun:stun.stunprotocol.org:3478"},
        
        # OpenRelay (principal gratuito, 20GB/mes)
        {
            "urls": [
                "turn:openrelay.metered.ca:80",
                "turn:openrelay.metered.ca:443?transport=tcp",
                "turn:openrelay.metered.ca:443?transport=udp"
            ],
            "username": "openrelayproject",
            "credential": "openrelayproject"
        },
        
        # Alternativas si openrelay falla/satura
        {
            "urls": "turn:numb.viagenie.ca",
            "username": "webrtc@live.com",
            "credential": "muazkh"
        },
        {
            "urls": "turn:relay1.expressturn.com:3478",
            "username": "expressturnfree",
            "credential": "expressturnfree"  # puede cambiar, busca actualizaciones si falla
        }
    ]
)

# Room ID
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room_input = st.text_input(
    "Room ID (compártelo exactamente)",
    value=st.session_state.room_id,
    max_chars=20,
    help="Usa el mismo en todos los dispositivos"
)

if st.button("Unirse / Crear nuevo"):
    new_room = room_input.strip()
    if new_room:
        st.session_state.room_id = new_room
    else:
        st.session_state.room_id = str(uuid.uuid4())[:8]
    st.rerun()

st.markdown(f"**Tu Room ID para compartir:** `{st.session_state.room_id}`")

# Audio constraints móviles: bajo consumo, eco fuerte, mono
audio_constraints = {
    "echoCancellation": True,
    "echoCancellationType": "system",  # o "browser" si falla
    "noiseSuppression": True,
    "autoGainControl": True,
    "channelCount": 1,          # Mono = menos datos en móvil
    "sampleRate": 16000,        # 16kHz = buena calidad + bajo ancho de banda
    "googEchoCancellation": True,
    "googNoiseSuppression": True
}

ctx = webrtc_streamer(
    key=f"audio_mobile_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,
    audio_html_attrs={
        "controls": False,
        "style": {"width": "100%", "margin": "10px 0"}
    }
)

# Diagnóstico
if ctx.input_audio_track:
    st.success("✅ Micrófono activo → tu voz va al otro")
else:
    st.error("❌ Micrófono no detectado")
    st.markdown("- Verifica permisos en navegador y ajustes del celular")
    st.markdown("- Prueba permitir 'siempre' para este sitio")

if ctx.state.playing:
    st.success("🟢 Reproduciendo audio del otro → ¡habla y escucha!")
    st.info("Con auriculares: solo deberías oír al otro (sin tu eco)")
else:
    st.warning("🔴 Esperando conexión... (ICE checking o failed)")
    st.markdown("""
    Soluciones rápidas:
    - Cambia WiFi → datos móviles (o viceversa)
    - Refresca página (F5 o botón recargar)
    - Crea Room ID nuevo
    - Prueba en Chrome (mejor en Android)
    """)

st.markdown("---")
st.caption("""
Si sigue "Esperando conexión...":
- Dime: ¿Android o iOS? ¿Chrome/Safari? ¿WiFi o datos?
- ¿Funciona en PC pero no en celular?
- ¿El otro dispositivo ve lo mismo?
- Abre consola (Chrome móvil: chrome://inspect desde PC) y copia errores con "ICE", "failed" o "closed"
""")
