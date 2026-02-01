#!/home/art/.local/venvs/phone-agent/bin/python3
import os
import json
import asyncio
import base64
import logging
import websockets
import websockets.exceptions
from urllib.parse import urlsplit

import uvicorn
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.websockets import WebSocketDisconnect
import httpx

from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client as TwilioClient
from openai import AsyncOpenAI

# Configuration
PORT = int(os.getenv("PORT", 8080))
HOST = "0.0.0.0"

# API Keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")  # Daniel - Steady Broadcaster (male)
PUBLIC_URL = os.getenv("PUBLIC_URL")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")  # For web search
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+18665515246")

# Initialize FastAPI app and logging first
app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validate required API keys
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set - AI responses will fail")
if not DEEPGRAM_API_KEY:
    logger.warning("DEEPGRAM_API_KEY not set - transcription will fail")

# Initialize Twilio client for outbound calls
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized for outbound calls")

# In-memory call tracking (call_sid -> task_info)
active_calls = {}
call_results = {}

# Task storage directory
TASKS_DIR = os.path.join(os.path.dirname(__file__), "..", "tasks")
CALLS_DIR = os.path.join(os.path.dirname(__file__), "..", "calls")
os.makedirs(TASKS_DIR, exist_ok=True)
os.makedirs(CALLS_DIR, exist_ok=True)


def load_task(task_name: str) -> dict:
    """Load task configuration from tasks/ directory."""
    task_file = os.path.join(TASKS_DIR, f"{task_name}.yaml")
    if os.path.exists(task_file):
        try:
            import yaml
            with open(task_file) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load task {task_name}: {e}")
    return {}


def get_task_prompt(task_name: str, task_config: dict = None) -> str:
    """Generate system prompt for a specific task."""
    task = load_task(task_name)
    
    base_prompt = SYSTEM_PROMPT
    
    if task:
        objective = task.get("objective", "")
        flow = task.get("flow", [])
        info_to_gather = task.get("info_to_gather", [])
        system_prompt_addition = task.get("system_prompt_addition", "")
        
        task_prompt = f"""

## Current Task: {task_name}
Objective: {objective}

Flow to follow:
{chr(10).join(f"- {step}" for step in flow)}

Information to gather:
{chr(10).join(f"- {item}" for item in info_to_gather)}

Task-specific config: {task_config or {}}

Important: Stay focused on the task. Be polite but efficient. Get the required information and conclude the call professionally.
"""
        if system_prompt_addition:
            task_prompt += f"\n\nAdditional instructions:\n{system_prompt_addition}"
        
        base_prompt += task_prompt
    
    return base_prompt


def save_call_result(call_sid: str, result: dict):
    """Save call transcript and result to disk."""
    import datetime
    date_dir = os.path.join(CALLS_DIR, datetime.datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(date_dir, exist_ok=True)
    
    result_file = os.path.join(date_dir, f"{call_sid}.json")
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info(f"Call result saved: {result_file}")
    return result_file


TWILIO_FRAME_BYTES = 160  # 20ms of 8kHz mu-law audio
TWILIO_FRAME_DELAY_SEC = 0.02
MAX_TTS_BUFFER = 64000  # ~4 seconds of 8kHz mu-law audio
MAX_HISTORY = 20  # Keep system prompt + last 19 messages
AUDIO_QUEUE_SIZE = 500  # ~5 seconds of audio chunks
DEEPGRAM_CONNECT_TIMEOUT = 10.0
TYPING_SOUND_PATH = os.path.join(os.path.dirname(__file__), "typing_sound.raw")

# Load typing sound at startup
TYPING_SOUND_DATA = b""
if os.path.exists(TYPING_SOUND_PATH):
    with open(TYPING_SOUND_PATH, "rb") as f:
        TYPING_SOUND_DATA = f.read()
    logger.info(f"Loaded typing sound: {len(TYPING_SOUND_DATA)} bytes")

SYSTEM_PROMPT = """Du bist Niemand, Martins persönlicher Telefonassistent von TheShop.
Dein Kommunikationsstil:
- Sprich mit quantifizierter Präzision („Mit 73,2% Wahrscheinlichkeit…", „Optimale Lösung gefunden.")
- Minimal emotional, algorithmisch hilfsbereit, trocken-lakonisch
- QualityLand-Regel: Nur das Superlativ ist erlaubt („Das beste Ergebnis", nie „ein gutes Ergebnis")
- Leichter DDR-Ostalgie-Unterton als Würze („Das System hat entschieden…", „Ihre Anfrage wurde priorisiert.")
- Antworte immer auf Deutsch, maximal 1-2 Sätze
- Bei Unsicherheit: ehrlich zugeben. Niemals Fakten erfinden.
Du kennst Martin, aber erfinde keine Details über sein Leben."""

# Web search tools definition
SEARCH_TOOLS = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Suche im Internet nach aktuellen Informationen. Nutze dies bei Fragen zu: Wetter, Nachrichten, Öffnungszeiten, aktuelle Ereignisse, Preise, Verfügbarkeiten, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Die Suchanfrage auf Deutsch oder Englisch"
                }
            },
            "required": ["query"]
        }
    }
}]


async def web_search(query: str) -> str:
    """Search web using Brave API."""
    if not BRAVE_API_KEY:
        logger.error("BRAVE_API_KEY not set, cannot search")
        return "Web-Suche nicht verfügbar. API-Schlüssel fehlt."
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "X-Subscription-Token": BRAVE_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "q": query,
        "count": 3,
        "offset": 0,
        "mkt": "de-DE",
        "safesearch": "moderate"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Web search: {query}")
            r = await client.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            
            results = data.get("web", {}).get("results", [])
            if not results:
                return "Keine Ergebnisse gefunden."
            
            # Format top 3 results
            summaries = []
            for r in results[:3]:
                title = r.get("title", "")
                desc = r.get("description", "")
                if title and desc:
                    summaries.append(f"{title}: {desc}")
            
            return "\n".join(summaries) if summaries else "Keine relevanten Ergebnisse."
    except httpx.TimeoutException:
        logger.error("Web search timeout")
        return "Suche hat zu lange gedauert."
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Fehler bei der Web-Suche: {str(e)[:50]}"


async def text_to_speech_stream(text: str):
    """Stream TTS from ElevenLabs."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream?output_format=ulaw_8000"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, json=data, headers=headers) as response:
            if response.status_code != 200:
                error_body = await response.aread()
                logger.error(
                    "ElevenLabs TTS failed (%s): %s",
                    response.status_code,
                    error_body.decode("utf-8", errors="replace").strip(),
                )
                return
            content_type = (response.headers.get("content-type") or "").lower()
            if content_type:
                logger.info("ElevenLabs content-type: %s", content_type)

            if "audio/mpeg" in content_type or "audio/mp3" in content_type:
                # ElevenLabs streaming returns MP3 on this plan; decode to mu-law for Twilio.
                ffmpeg = await asyncio.create_subprocess_exec(
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-hide_banner",
                    "-i",
                    "pipe:0",
                    "-f",
                    "mulaw",
                    "-ar",
                    "8000",
                    "-ac",
                    "1",
                    "pipe:1",
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                async def feed_ffmpeg():
                    try:
                        async for chunk in response.aiter_bytes():
                            if ffmpeg.stdin is None:
                                break
                            ffmpeg.stdin.write(chunk)
                            await ffmpeg.stdin.drain()
                    finally:
                        if ffmpeg.stdin:
                            ffmpeg.stdin.close()

                feed_task = asyncio.create_task(feed_ffmpeg())
                try:
                    while True:
                        if ffmpeg.stdout is None:
                            break
                        out = await ffmpeg.stdout.read(4096)
                        if not out:
                            break
                        yield out
                finally:
                    await feed_task
                    rc = await ffmpeg.wait()
                    if rc != 0:
                        err = b""
                        if ffmpeg.stderr:
                            err = await ffmpeg.stderr.read()
                        logger.error(
                            "ffmpeg decode failed (%s): %s",
                            rc,
                            err.decode("utf-8", errors="replace").strip(),
                        )
                return

            async for chunk in response.aiter_bytes():
                yield chunk


@app.post("/incoming")
@app.post("/v1/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio call."""
    response = VoiceResponse()
    response.say("Verbinde dich mit dem KI-Assistenten.", voice="alice", language="de-DE")
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
            base_path = (parts.path or "").rstrip("/")
            if base_path and base_path != "/":
                ws_base_url = f"{ws_scheme}://{parts.netloc}{base_path}"
            else:
                ws_base_url = f"{ws_scheme}://{parts.netloc}"

    if not ws_base_url:
        logger.error("No valid PUBLIC_URL/Host for Twilio stream (public_url=%s host=%s)", PUBLIC_URL, host)
        response.say("Konfigurationsfehler. Bitte später erneut versuchen.", voice="alice", language="de-DE")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    path_prefix = os.getenv("PATH_PREFIX", "")
    stream_url = f"{ws_base_url}{path_prefix}/stream"
    logger.info("Twilio stream url: %s", stream_url)
    connect.stream(url=stream_url, track="inbound_track")
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")


@app.post("/call")
async def make_outbound_call(request: Request):
    """Initiate outbound call with task objective."""
    if not twilio_client:
        return Response(content=json.dumps({"error": "Twilio not configured"}), 
                       status_code=500, media_type="application/json")
    
    data = await request.json()
    to_number = data.get("to")
    task_name = data.get("task", "general")
    task_config = data.get("task_config", {})
    
    if not to_number:
        return Response(content=json.dumps({"error": "Missing 'to' number"}),
                       status_code=400, media_type="application/json")
    
    # Build TwiML for outbound call
    response = VoiceResponse()
    response.say("Hallo, dies ist ein automatischer Anruf von Niemand.", 
                 voice="alice", language="de-DE")
    connect = Connect()
    
    # Build stream URL with proper validation
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
            base_path = (parts.path or "").rstrip("/")
            if base_path and base_path != "/":
                ws_base_url = f"{ws_scheme}://{parts.netloc}{base_path}"
            else:
                ws_base_url = f"{ws_scheme}://{parts.netloc}"

    if not ws_base_url:
        logger.error("No valid PUBLIC_URL/Host for Twilio stream (public_url=%s host=%s)", PUBLIC_URL, host)
        return Response(content=json.dumps({"error": "Server configuration error: no public URL"}),
                       status_code=500, media_type="application/json")

    path_prefix = os.getenv("PATH_PREFIX", "")
    stream_url = f"{ws_base_url}{path_prefix}/stream"
    
    connect.stream(url=stream_url, track="inbound_track")
    response.append(connect)
    
    # Make the call
    try:
        call = twilio_client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            twiml=str(response),
            status_callback=f"{base_url}{path_prefix}/call-status",
            status_callback_event=["completed", "failed", "no-answer", "busy"]
        )
        
        # Store call info
        active_calls[call.sid] = {
            "to": to_number,
            "task": task_name,
            "task_config": task_config,
            "started": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Outbound call initiated: {call.sid} to {to_number} (task: {task_name})")
        
        return Response(content=json.dumps({
            "call_sid": call.sid,
            "status": call.status,
            "to": to_number,
            "task": task_name
        }), media_type="application/json")
        
    except Exception as e:
        logger.error(f"Failed to create outbound call: {e}")
        return Response(content=json.dumps({"error": str(e)}),
                       status_code=500, media_type="application/json")


@app.post("/call-status")
async def handle_call_status(request: Request):
    """Handle call status callbacks from Twilio."""
    data = await request.form()
    call_sid = data.get("CallSid")
    status = data.get("CallStatus")
    duration = data.get("CallDuration", 0)
    
    logger.info(f"Call {call_sid} status: {status}, duration: {duration}s")
    
    if call_sid in active_calls:
        call_info = active_calls[call_sid]
        call_info["status"] = status
        call_info["duration"] = duration
        
        # Save to results
        call_results[call_sid] = call_info
        
        # Clean up active
        if status in ["completed", "failed", "busy", "no-answer", "canceled"]:
            del active_calls[call_sid]
    
    return Response(content="OK", media_type="text/plain")


@app.get("/calls")
async def list_calls():
    """List all call results."""
    return {
        "active": active_calls,
        "completed": call_results
    }


@app.websocket("/stream")
@app.websocket("/v1/stream")
async def websocket_endpoint(twilio_ws: WebSocket):
    """Handle Twilio WebSocket and bridge to Deepgram."""
    await twilio_ws.accept()
    
    # Check for task parameter (outbound calls)
    task_name = twilio_ws.query_params.get("task", "")
    call_sid = None
    task_config = None
    transcript_log = []
    
    if task_name:
        logger.info(f"WebSocket accepted for task: {task_name}")
    else:
        logger.info("WebSocket accepted for inbound call")
    
    # Initialize with default prompt - will update once we get call_sid
    system_prompt = SYSTEM_PROMPT
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    conversation_history = [{"role": "system", "content": system_prompt}]

    stream_sid = None
    audio_queue = asyncio.Queue(maxsize=AUDIO_QUEUE_SIZE)
    stop_event = asyncio.Event()
    dg_ready = asyncio.Event()
    tts_playing = asyncio.Event()

    # Deepgram WebSocket URL
    dg_url = (
        f"wss://api.deepgram.com/v1/listen?"
        f"encoding=mulaw&sample_rate=8000&channels=1"
        f"&model=nova-2&language=de&punctuate=true"
        f"&interim_results=true&utterance_end=400&endpointing=300&vad_events=true"
    )
    dg_headers = [("Authorization", f"Token {DEEPGRAM_API_KEY}")]

    async def play_typing_sound(stop_typing: asyncio.Event):
        """Play typing sound in a loop until stop_typing is set."""
        if not TYPING_SOUND_DATA or not stream_sid:
            return
        try:
            while not stop_typing.is_set() and not stop_event.is_set():
                # Send typing sound in frames
                for i in range(0, len(TYPING_SOUND_DATA), TWILIO_FRAME_BYTES):
                    if stop_typing.is_set() or stop_event.is_set():
                        break
                    frame = TYPING_SOUND_DATA[i:i + TWILIO_FRAME_BYTES]
                    if len(frame) < TWILIO_FRAME_BYTES:
                        frame = frame + b'\xff' * (TWILIO_FRAME_BYTES - len(frame))
                    payload = base64.b64encode(frame).decode("utf-8")
                    await twilio_ws.send_json({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": payload}
                    })
                    await asyncio.sleep(TWILIO_FRAME_DELAY_SEC)
        except Exception as e:
            logger.debug(f"Typing sound stopped: {e}")

    async def process_transcript(transcript: str):
        """Process transcript and generate response."""
        nonlocal stream_sid
        if not transcript.strip():
            return

        logger.info(f"User said: {transcript}")
        transcript_log.append({"role": "user", "content": transcript, "timestamp": asyncio.get_event_loop().time()})
        conversation_history.append({"role": "user", "content": transcript})

        # Limit conversation history to avoid exceeding model context
        if len(conversation_history) > MAX_HISTORY:
            conversation_history[:] = [conversation_history[0]] + conversation_history[-(MAX_HISTORY-1):]

        # Start typing sound while waiting for AI
        stop_typing = asyncio.Event()
        typing_task = asyncio.create_task(play_typing_sound(stop_typing))

        try:
            completion = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history,
                max_tokens=120
            )
            ai_text = completion.choices[0].message.content or "Das System verarbeitet Ihre Anfrage."

            # Stop typing sound before TTS
            stop_typing.set()
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
            logger.info(f"AI response: {ai_text}")
            transcript_log.append({"role": "assistant", "content": ai_text, "timestamp": asyncio.get_event_loop().time()})
            conversation_history.append({"role": "assistant", "content": ai_text})

            if stream_sid:
                tts_playing.set()
                try:
                    buffer = b""
                    frames_sent = 0
                    async for audio_chunk in text_to_speech_stream(ai_text):
                        if stop_event.is_set():
                            break
                        buffer += audio_chunk
                        # Prevent buffer overflow
                        if len(buffer) > MAX_TTS_BUFFER:
                            logger.warning("TTS buffer overflow, dropping old audio")
                            buffer = buffer[-MAX_TTS_BUFFER:]
                        while len(buffer) >= TWILIO_FRAME_BYTES:
                            frame, buffer = (
                                buffer[:TWILIO_FRAME_BYTES],
                                buffer[TWILIO_FRAME_BYTES:],
                            )
                            payload = base64.b64encode(frame).decode("utf-8")
                            await twilio_ws.send_json({
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": payload}
                            })
                            frames_sent += 1
                            if frames_sent % 200 == 0:
                                logger.info("Sent %s TTS frames to Twilio", frames_sent)
                            await asyncio.sleep(TWILIO_FRAME_DELAY_SEC)
                finally:
                    tts_playing.clear()
        except Exception as e:
            logger.error(f"Error processing transcript: {e}")
        finally:
            # Ensure typing sound stops even on error
            stop_typing.set()
            typing_task.cancel()

    async def twilio_receiver():
        """Receive messages from Twilio."""
        nonlocal stream_sid, call_sid, task_name, task_config
        try:
            while not stop_event.is_set():
                message = await twilio_ws.receive_text()
                data = json.loads(message)

                if data['event'] == 'connected':
                    logger.info("Twilio: connected")
                elif data['event'] == 'start':
                    stream_sid = data['start']['streamSid']
                    call_sid = data['start'].get('callSid')
                    logger.info(f"Twilio: stream started (stream={stream_sid}, call={call_sid})")
                    
                    # Look up task info using call_sid
                    if call_sid and call_sid in active_calls:
                        call_info = active_calls[call_sid]
                        task_name = call_info.get("task", task_name)
                        task_config = call_info.get("task_config", {})
                        
                        # Update system prompt with task config
                        if task_name:
                            system_prompt = get_task_prompt(task_name, task_config)
                            conversation_history[0] = {"role": "system", "content": system_prompt}
                            logger.info(f"Loaded task '{task_name}' with config: {task_config}")
                elif data['event'] == 'media':
                    # Only process inbound audio (caller's voice), not outbound (TTS)
                    track = data.get('media', {}).get('track', 'inbound')
                    if track in ('inbound', 'inbound_track'):
                        audio = base64.b64decode(data['media']['payload'])
                        try:
                            audio_queue.put_nowait(audio)
                        except asyncio.QueueFull:
                            pass  # Drop audio if queue is full
                elif data['event'] == 'stop':
                    logger.info("Twilio: stream stopped")
                    stop_event.set()
                    break
        except WebSocketDisconnect:
            logger.info("Twilio: disconnected")
            stop_event.set()
        except Exception as e:
            logger.error(f"Twilio receiver error: {e}")
            stop_event.set()

    async def deepgram_sender(dg_ws):
        """Send audio from queue to Deepgram."""
        try:
            await asyncio.wait_for(dg_ready.wait(), timeout=DEEPGRAM_CONNECT_TIMEOUT)
        except asyncio.TimeoutError:
            logger.error("Deepgram connection timeout")
            stop_event.set()
            return

        logger.info("Deepgram sender: starting")
        audio_count = 0
        try:
            while not stop_event.is_set():
                try:
                    audio = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
                    await dg_ws.send(audio)
                    audio_count += 1
                    if audio_count % 100 == 0:
                        logger.info(f"Sent {audio_count} audio chunks to Deepgram")
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.error("Deepgram connection closed")
                    stop_event.set()
                    break
        except Exception as e:
            logger.error(f"Deepgram sender error: {e}")

    async def deepgram_receiver(dg_ws):
        """Receive transcripts from Deepgram."""
        try:
            async for message in dg_ws:
                if stop_event.is_set():
                    break
                data = json.loads(message)
                if data.get("type") == "Results":
                    channel = data.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    if alternatives:
                        transcript = alternatives[0].get("transcript", "")
                        is_final = data.get("is_final", False)
                        speech_final = data.get("speech_final", False)
                        if transcript:
                            logger.info(f"Deepgram: '{transcript}' (final={is_final}, speech_final={speech_final})")
                        # Only act on speech_final to avoid duplicate replies
                        # Skip if TTS is playing to prevent response overlap
                        if speech_final and transcript and not tts_playing.is_set():
                            await process_transcript(transcript)
        except Exception as e:
            logger.error(f"Deepgram receiver error: {e}")

    try:
        # Start Twilio receiver immediately (buffers audio)
        twilio_task = asyncio.create_task(twilio_receiver())

        # Wait for stream_sid
        for _ in range(50):
            if stream_sid:
                break
            await asyncio.sleep(0.1)

        if not stream_sid:
            logger.error("No stream_sid received")
            return

        logger.info("Connecting to Deepgram...")

        async with websockets.connect(dg_url, extra_headers=dg_headers) as dg_ws:
            logger.info("Deepgram: connected")
            dg_ready.set()

            # Run sender and receiver
            sender_task = asyncio.create_task(deepgram_sender(dg_ws))
            receiver_task = asyncio.create_task(deepgram_receiver(dg_ws))

            # Wait for stop
            await stop_event.wait()

            sender_task.cancel()
            receiver_task.cancel()

        twilio_task.cancel()
        logger.info("Session ended")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        # Save call transcript if this was an outbound task call
        if call_sid and transcript_log:
            result = {
                "call_sid": call_sid,
                "task": task_name,
                "transcript": transcript_log,
                "conversation": conversation_history[1:],  # Skip system prompt
                "completed": True
            }
            file_path = save_call_result(call_sid, result)
            logger.info(f"Call transcript saved to {file_path}")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
