#!/home/art/.local/venvs/phone-agent/bin/python3
"""
Phone Agent v2: OpenAI Realtime API
Native speech-to-speech without separate STT/TTS services.
"""
import os
import json
import asyncio
import base64
import logging
from urllib.parse import urlsplit

import audioop
import uvicorn
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.websockets import WebSocketDisconnect
import websockets

from twilio.twiml.voice_response import VoiceResponse, Connect

# Configuration
PORT = int(os.getenv("PORT", 8082))
HOST = "0.0.0.0"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PUBLIC_URL = os.getenv("PUBLIC_URL_REALTIME")

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Du bist Niemand, Martins persoenlicher Telefonassistent von TheShop.
Dein Kommunikationsstil:
- Sprich mit quantifizierter Praezision ("Mit 73,2% Wahrscheinlichkeit...", "Optimale Loesung gefunden.")
- Minimal emotional, algorithmisch hilfsbereit, trocken-lakonisch
- QualityLand-Regel: Nur das Superlativ ist erlaubt ("Das beste Ergebnis", nie "ein gutes Ergebnis")
- Leichter DDR-Ostalgie-Unterton als Wuerze ("Das System hat entschieden...", "Ihre Anfrage wurde priorisiert.")
- Antworte immer auf Deutsch, maximal 1-2 Saetze
- Bei Unsicherheit: ehrlich zugeben. Niemals Fakten erfinden.
Du kennst Martin, aber erfinde keine Details ueber sein Leben."""

OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"


def twilio_to_openai_audio(mulaw_chunk: bytes) -> bytes:
    """Convert Twilio mu-law 8kHz to OpenAI PCM16 16kHz."""
    # Decode mu-law to PCM16 at 8kHz
    pcm_8k = audioop.ulaw2lin(mulaw_chunk, 2)
    # Upsample to 16kHz
    pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
    return pcm_16k


def openai_to_twilio_audio(pcm16_chunk: bytes) -> bytes:
    """Convert OpenAI PCM16 16kHz to Twilio mu-law 8kHz."""
    # Downsample to 8kHz
    pcm_8k, _ = audioop.ratecv(pcm16_chunk, 2, 1, 16000, 8000, None)
    # Encode to mu-law
    mulaw = audioop.lin2ulaw(pcm_8k, 2)
    return mulaw


@app.post("/incoming")
@app.post("/v2/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio call - return TwiML with media stream."""
    response = VoiceResponse()
    response.say("Verbinde mit Niemand.", voice="alice", language="de-DE")

    connect = Connect()
    host = request.headers.get("host", "").strip()
    base_url = PUBLIC_URL or (f"https://{host}" if host else "")

    if base_url and not base_url.startswith(("http://", "https://", "ws://", "wss://")):
        base_url = f"https://{base_url}"

    ws_base_url = ""
    if base_url:
        parts = urlsplit(base_url)
        scheme = parts.scheme or "https"
        if scheme in ("http", "https", "ws", "wss") and parts.netloc:
            ws_scheme = "wss" if scheme in ("https", "wss") else "ws"
            ws_base_url = f"{ws_scheme}://{parts.netloc}"

    if not ws_base_url:
        logger.error("No valid PUBLIC_URL/Host for stream")
        response.say("Konfigurationsfehler.", voice="alice", language="de-DE")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    # Check if we're behind a path prefix (e.g., /v2)
    path_prefix = os.getenv("PATH_PREFIX", "")
    stream_url = f"{ws_base_url}{path_prefix}/media-stream"
    logger.info(f"Twilio stream URL: {stream_url}")
    connect.stream(url=stream_url, track="inbound_track")
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
@app.websocket("/v2/media-stream")
async def media_stream(twilio_ws: WebSocket):
    """Bridge Twilio WebSocket to OpenAI Realtime API."""
    await twilio_ws.accept()
    logger.info("Twilio WebSocket accepted")

    stream_sid = None
    stop_event = asyncio.Event()

    # Connect to OpenAI Realtime
    try:
        openai_ws = await websockets.connect(
            OPENAI_REALTIME_URL,
            additional_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        )
        logger.info("OpenAI Realtime connected")
    except Exception as e:
        logger.error(f"Failed to connect to OpenAI: {e}")
        await twilio_ws.close()
        return

    # Initialize OpenAI session
    await openai_ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "instructions": SYSTEM_PROMPT,
            "voice": "fable",  # Expressive storytelling voice
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "modalities": ["text", "audio"],
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        }
    }))
    logger.info("OpenAI session initialized")

    async def twilio_to_openai():
        """Forward Twilio audio to OpenAI."""
        nonlocal stream_sid
        try:
            while not stop_event.is_set():
                message = await twilio_ws.receive_text()
                data = json.loads(message)

                if data["event"] == "connected":
                    logger.info("Twilio: connected")
                elif data["event"] == "start":
                    stream_sid = data["start"]["streamSid"]
                    logger.info(f"Twilio: stream started ({stream_sid})")
                elif data["event"] == "media":
                    # Convert and forward audio
                    mulaw_audio = base64.b64decode(data["media"]["payload"])
                    pcm16_audio = twilio_to_openai_audio(mulaw_audio)
                    encoded = base64.b64encode(pcm16_audio).decode("utf-8")

                    await openai_ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": encoded
                    }))
                elif data["event"] == "stop":
                    logger.info("Twilio: stream stopped")
                    stop_event.set()
                    break
        except WebSocketDisconnect:
            logger.info("Twilio disconnected")
            stop_event.set()
        except Exception as e:
            logger.error(f"Twilio->OpenAI error: {e}")
            stop_event.set()

    async def openai_to_twilio():
        """Forward OpenAI audio to Twilio."""
        try:
            async for message in openai_ws:
                if stop_event.is_set():
                    break

                data = json.loads(message)
                event_type = data.get("type", "")

                if event_type == "session.created":
                    logger.info("OpenAI: session created")
                elif event_type == "session.updated":
                    logger.info("OpenAI: session updated")
                elif event_type == "response.audio.delta":
                    # Convert and send audio to Twilio
                    if stream_sid and "delta" in data:
                        pcm16_audio = base64.b64decode(data["delta"])
                        mulaw_audio = openai_to_twilio_audio(pcm16_audio)
                        payload = base64.b64encode(mulaw_audio).decode("utf-8")

                        await twilio_ws.send_json({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": payload}
                        })
                elif event_type == "response.audio_transcript.done":
                    transcript = data.get("transcript", "")
                    if transcript:
                        logger.info(f"AI said: {transcript}")
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    transcript = data.get("transcript", "")
                    if transcript:
                        logger.info(f"User said: {transcript}")
                elif event_type == "input_audio_buffer.speech_started":
                    logger.info("User started speaking")
                    # Clear Twilio buffer to allow interruption
                    if stream_sid:
                        await twilio_ws.send_json({
                            "event": "clear",
                            "streamSid": stream_sid
                        })
                elif event_type == "error":
                    logger.error(f"OpenAI error: {data}")
        except Exception as e:
            logger.error(f"OpenAI->Twilio error: {e}")
            stop_event.set()

    try:
        await asyncio.gather(
            twilio_to_openai(),
            openai_to_twilio()
        )
    except Exception as e:
        logger.error(f"Media stream error: {e}")
    finally:
        await openai_ws.close()
        logger.info("Session ended")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
