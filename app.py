import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoHTMLAttributes, AudioHTMLAttributes
import uuid

st.set_page_config(
    page_title="Llamada de Audio Privada (1 a 1)",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📞 Llamada de Audio Privada")
st.caption("1 a 1 – Solo audio – Usa auriculares – Toca 'Desbloquear Sonido' si no oyes nada")

st.markdown("""
**Instrucciones obligatorias para que suene el audio del otro:**
1. **Usa auriculares** (con cable preferiblemente – evita eco y routing raro).
2. Permite micrófono.
3. Ambos deben dar clic en **"Unirse y activar llamada"**.
4. **En celular**: después de conectar, **toca varias veces la pantalla** o el botón grande **"Desbloquear Sonido"** (esto es clave para desbloquear autoplay en Chrome/Safari móvil).
5. Habla fuerte en un lado → el otro debería oírte después del clic.
6. Si no suena: refresca, cambia red (WiFi ↔ datos), prueba Chrome (Android) o Safari (iPhone).
""")

RTC_CONFIG = RTCConfiguration(
    iceServers=[
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun.stunprotocol.org:3478"},
        {
            "urls": [
                "turn:openrelay.metered.ca:80",
                "turn:openrelay.metered.ca:443?transport=tcp",
                "turn:openrelay.metered.ca:443?transport=udp"
            ],
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

if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room_input = st.text_input(
    "Room ID (compártelo exactamente)",
    value=st.session_state.room_id,
    max_chars=20
)

if st.button("Unirse y activar llamada"):
    cleaned = room_input.strip()
    if cleaned:
        st.session_state.room_id = cleaned
    st.rerun()

st.markdown(f"**Room ID para compartir:** `{st.session_state.room_id}`")

audio_constraints = {
    "echoCancellation": True,
    "echoCancellationType": "system",
    "noiseSuppression": True,
    "autoGainControl": True,
    "channelCount": 1,
    "sampleRate": 16000
}

ctx = webrtc_streamer(
    key=f"llamada_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,
    audio_html_attrs=AudioHTMLAttributes(
        auto_play=True,
        controls=False,
        muted=False,          # importante: no muted por defecto
        style={"width": "100%", "margin": "15px 0"}
    )
)

# Diagnóstico y desbloqueo explícito (clave para móviles)
if ctx.input_audio_track:
    st.success("✅ Micrófono enviando voz al otro")
else:
    st.error("❌ No detecta micrófono – permite acceso")

if ctx.state.playing:
    st.success("🟢 Conectado – audio debería reproducirse")
    st.markdown("**Si no oyes nada:**")
    st.markdown("- Toca la pantalla varias veces")
    st.markdown("- Usa auriculares")
    st.markdown("- Habla fuerte en el otro lado")
    if st.button("🔊 DESBLOQUEAR SONIDO (toca aquí en celular si silencioso)", use_container_width=True, type="primary"):
        st.info("Clic realizado → esto debería desbloquear el audio remoto. Habla ahora en el otro dispositivo.")
else:
    st.warning("🔴 Esperando conexión completa... (prueba cambiar red o refrescar)")

st.markdown("---")
st.caption("""
Realidad 2026: streamlit-webrtc tiene limitaciones en móviles por autoplay y red. 
Si después del clic + auriculares + hablar fuerte sigue sin sonido en ninguno de los lados → 
la herramienta no es confiable para llamadas reales en tu entorno (Cloud + red SV).
Alternativa dentro de Streamlit: iframe de Jitsi Meet gratuito (funciona siempre).
¿Quieres que te dé esa versión con iframe? Es mucho más estable para llamadas.
""")
