#!/usr/bin/env python3
"""
ClipIt - Semantic Audio Extraction
Find and cut audio segments using natural language queries.
"""

import os
import sys
import json
import argparse
import subprocess
import requests
import tempfile
from typing import Optional, Dict, Any, List

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "-q"])
    from openai import OpenAI

# Constants
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/speech-to-text"

def get_keys():
    """Ensure API keys are present."""
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    missing = []
    if not eleven_key:
        missing.append("ELEVENLABS_API_KEY")
    if not openai_key:
        missing.append("OPENAI_API_KEY")
    
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    return eleven_key, openai_key

def transcribe_audio(filepath: str, api_key: str) -> Dict[str, Any]:
    """
    Transcribe audio using ElevenLabs Scribe API.
    """
    print(f"Transcribing {os.path.basename(filepath)}...")
    
    headers = {
        "xi-api-key": api_key
    }
    
    files = {
        'file': open(filepath, 'rb')
    }
    
    data = {
        'model_id': 'scribe_v1',
        'tag_audio_events': 'true'
    }

    try:
        response = requests.post(ELEVENLABS_API_URL, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error during transcription: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"API Response: {e.response.text}")
        sys.exit(1)
    finally:
        files['file'].close()

def find_segment(transcript_data: Dict[str, Any], query: str, api_key: str) -> Dict[str, float]:
    """
    Use OpenAI to find the start and end timestamps for the query.
    """
    print("Analyzing transcript...")
    
    client = OpenAI(api_key=api_key)
    
    # Prepare a compact representation of the transcript for the model
    # Format: "word (start-end)" to save tokens while keeping precision
    words = transcript_data.get('words', [])
    
    # Check token count - if clear text is too long, we might need a sliding window or summary strategy
    # For now, we assume reasonable length clips or high context models (GPT-4o)
    
    transcript_text = ""
    for w in words:
        if w['type'] == 'word':
            transcript_text += f"{w['text']} "
    
    # We pass the full word list in a structured way so the model can look up exact timestamps
    # To save space, we'll map words to IDs or just pass a simplified list
    detailed_transcript = []
    for i, w in enumerate(words):
        if w['type'] == 'word':
            detailed_transcript.append({
                "text": w['text'],
                "start": w['start'],
                "end": w['end']
            })
            
    # System prompt
    system_prompt = """You are an expert video editor.
    Your task is to identify the best logical segment in the transcript that matches the user's intent.
    
    CRITICAL INSTRUCTION:
    1. **Sentence Alignment**: You MUST start the clip at the beginning of the sentence. If the query matches the middle of a sentence, BACKTRACK to the start of that sentence.
       - Incorrect: "...science notebook." (starts mid-sentence)
       - Correct: "Keep a science notebook." (starts at sentence boundary)
    2. **Context**: Include the full thought. Do not cut off mid-sentence.
    3. **Mapping**: Use the provided "Full Transcript Text" to find the sentence boundaries (punctuation), then use the "Word Timestamps" to find the exact time.
    
    Input provided:
    1. Full Transcript Text (with punctuation).
    2. Word Timestamps (list of words with start/end times).
    3. User Query.
    
    Output requirement:
    Return strictly valid JSON with 'start' and 'end' keys in seconds.
    Example: {"start": 12.5, "end": 18.2}
    """
    
    full_text = transcript_data.get('text', '')
    
    user_content = f"""
    Query: "{query}"
    
    Full Transcript Text:
    {full_text}
    
    Word Timestamps:
    {json.dumps(detailed_transcript, ensure_ascii=False)}
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # efficient and capable
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Error analyzing transcript: {e}")
        sys.exit(1)



def get_extension_from_headers(response) -> str:
    """Attempt to guess extension from Content-Type or Content-Disposition."""
    import mimetypes
    content_type = response.headers.get("Content-Type")
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(';')[0].strip())
        if ext:
            return ext
    return ""

def download_file(url: str) -> str:
    """
    Download a file from a URL to a temporary file.
    """
    print(f"Downloading media from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Try to determine extension
        ext = os.path.splitext(url)[1].split('?')[0]
        if not ext:
            ext = get_extension_from_headers(response)
        if not ext:
            ext = ".mp3" # Fallback
            
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"Downloaded to {temp_path}")
        return temp_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

def is_video_file(path: str) -> bool:
    """Check if file has a video extension."""
    video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
    _, ext = os.path.splitext(path)
    return ext.lower() in video_exts

def extract_audio(video_path: str) -> str:
    """Extract audio track from video to a temp mp3 file."""
    print("Extracting audio track from video...")
    fd, temp_audio = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn", # Disable video
        "-acodec", "libmp3lame",
        "-q:a", "2",
        "-loglevel", "error",
        temp_audio
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return temp_audio
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        sys.exit(1)

def cut_media(filepath: str, start: float, end: float, output_path: str, is_video: bool = False):
    """
    Cut the media file using ffmpeg. Re-encodes to ensure precision.
    """
    print(f"Cutting {'video' if is_video else 'audio'} from {start:.2f}s to {end:.2f}s...")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", filepath
    ]
    
    if is_video:
        # Video encoding settings
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-strict", "experimental"
        ])
    else:
        # Audio encoding settings
        cmd.extend([
            "-c:a", "libmp3lame",
            "-q:a", "2"
        ])
        
    cmd.extend(["-loglevel", "error", output_path])
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Success! Clip saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        sys.exit(1)

def is_youtube_url(url: str) -> bool:
    """Check if URL is from YouTube."""
    return "youtube.com" in url or "youtu.be" in url

def download_youtube_video(url: str) -> str:
    """Download video from YouTube using yt-dlp."""
    print(f"Downloading YouTube video from {url}...")
    try:
        import yt_dlp
    except ImportError:
        print("Installing yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
        import yt_dlp

    # Create a temp directory to store the download
    temp_dir = tempfile.mkdtemp()
    
    # Use 'android' client which is often more robust against 403s
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        print("\nTip: YouTube often updates their anti-bot protections. Try upgrading yt-dlp:")
        print(f"     {sys.executable} -m pip install --upgrade yt-dlp")
        sys.exit(1)

def dub_media(filepath: str, target_lang: str, api_key: str, output_path: str):
    """
    Dub the media file using ElevenLabs Dubbing API.
    """
    print(f"Starting dubbing to '{target_lang}'...")
    
    url_create = "https://api.elevenlabs.io/v1/dubbing"
    headers = {"xi-api-key": api_key}
    
    # 1. Create Dubbing Project
    print("Uploading file for dubbing...")
    
    # MIME detection
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = "video/mp4" if filepath.lower().endswith(('.mp4', '.mov', '.avi')) else "audio/mpeg"
        
    def create_job(watermark_setting: bool):
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f, mime_type)}
            data = {
                "mode": "automatic",
                "target_lang": target_lang,
                "source_lang": "auto",
                "num_speakers": 1,
                "watermark": watermark_setting
            }
            return requests.post(url_create, headers=headers, files=files, data=data)

    try:
        # Try without watermark first (cleaner result)
        response = create_job(False)
        
        # If rejected due to watermark policy (400), retry with watermark
        if response.status_code == 400 and "watermark" in response.text.lower():
            print("Watermark required for this plan. Retrying with watermark...")
            response = create_job(True)
            
        response.raise_for_status()
        dubbing_id = response.json().get("dubbing_id")
        print(f"Dubbing job created: {dubbing_id}")
        
    except Exception as e:
        print(f"Error creating dubbing job: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)
        return

    # 2. Poll for completion
    import time
    print("Waiting for dubbing to complete...")
    url_status = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}"
    
    while True:
        try:
            res = requests.get(url_status, headers=headers)
            res.raise_for_status()
            status = res.json().get("status")
            
            if status == "dubbed":
                print("Dubbing complete!")
                break
            elif status == "failed":
                error_detail = res.json().get("error_detail", "Unknown error")
                print(f"Dubbing failed: {error_detail}")
                return
            else:
                print(f"Status: {status}...", end="\r")
                time.sleep(2)
        except Exception as e:
            print(f"Error checking status: {e}")
            return

    # 3. Download Result
    print(f"Downloading dubbed file to {output_path}...")
    url_download = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{target_lang}"
    
    try:
        res = requests.get(url_download, headers=headers)
        res.raise_for_status()
        
        # Check if we need to adjust extension based on content-type?
        # For now, we respect the user's requested output path, but warn if mismatch?
        # Actually, let's just write bytes.
        
        with open(output_path, "wb") as f:
            f.write(res.content)
            
        print("Success! Dubbed file saved.")
        
    except Exception as e:
        print(f"Error downloading dubbed file: {e}")


def isolate_audio(filepath: str, api_key: str, output_path: str):
    """
    Isolate audio (remove noise) using ElevenLabs Audio Isolation API.
    """
    print("Isolating audio (removing background noise)...")
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        print("Installing elevenlabs package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "elevenlabs", "-q"])
        from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)
    
    try:
        # Read the file
        with open(filepath, "rb") as f:
            audio_data = f.read()
            
        # Call API (using iterator to write chunks)
        audio_stream = client.audio_isolation.audio_isolation(audio=audio_data)
        
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
                
        print(f"Success! Isolated audio saved to {output_path}")
        
    except Exception as e:
        print(f"Error isolating audio: {e}")
        # Fallback using requests if library method fails or changes
        print("Retrying with direct API call...")
        try:
             url = "https://api.elevenlabs.io/v1/audio-isolation"
             headers = {"xi-api-key": api_key}
             files = {"audio": open(filepath, "rb")}
             response = requests.post(url, headers=headers, files=files, stream=True)
             response.raise_for_status()
             with open(output_path, "wb") as f:
                 for chunk in response.iter_content(chunk_size=4096):
                     f.write(chunk)
             print(f"Success! Isolated audio saved to {output_path} (via fallback)")
        except Exception as e2:
             print(f"Error isolating audio (fallback): {e2}")


def replace_audio_in_video(video_path: str, new_audio_path: str, output_path: str):
    """
    Replace the audio track of a video with a new audio file using ffmpeg.
    """
    print("Merging isolated audio back into video...")
    # ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest output.mp4
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", new_audio_path,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-loglevel", "error",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Success! Merged video saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio/video: {e}")

def main():
    parser = argparse.ArgumentParser(description="ClipHunt - Find and cut audio/video clips")
    parser.add_argument("--input", "-i", required=True, help="Input file path or URL")
    parser.add_argument("--query", "-q", required=True, help="Description of the clip to find")
    parser.add_argument("--output", "-o", help="Output file path (default: derived from input)")
    parser.add_argument("--context", "-c", type=float, default=0.0, help="Padding in seconds")
    parser.add_argument("--dub", "-d", help="Target language code for dubbing (e.g. 'es', 'fr', 'hi')")
    parser.add_argument("--isolate", action="store_true", help="Remove background noise using Audio Isolation")
    
    args = parser.parse_args()
    
    input_path = args.input
    is_temp = False
    temp_audio_path = None
    
    # Check if input is a URL
    if input_path.startswith(('http://', 'https://')):
        if is_youtube_url(input_path):
            input_path = download_youtube_video(input_path)
            is_temp = True
        else:
            input_path = download_file(input_path)
            is_temp = True
    elif not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    try:
        is_video = is_video_file(input_path)
        
        # Determine output filename if not provided
        if not args.output:
            _, ext = os.path.splitext(input_path)
            args.output = f"clip{ext}"
            
        eleven_key, openai_key = get_keys()
        
        # Prepare source for transcription
        transcription_source = input_path
        if is_video:
            temp_audio_path = extract_audio(input_path)
            transcription_source = temp_audio_path
            
        # 1. Transcribe
        transcript = transcribe_audio(transcription_source, eleven_key)
        
        # 2. Analyze
        timestamps = find_segment(transcript, args.query, openai_key)
        
        if not timestamps or 'start' not in timestamps or 'end' not in timestamps:
            print("Could not find matching segment.")
            sys.exit(1)
            
        start_time = max(0.0, timestamps['start'] - args.context)
        end_time = timestamps['end'] + args.context
        
        print(f"Found segment: {start_time:.2f}s - {end_time:.2f}s")
        
        # 3. Cut
        cut_media(input_path, start_time, end_time, args.output, is_video=is_video)
        
        current_output = args.output
        
        # 4. Isolate (Optional)
        if args.isolate:
            isolated_output = os.path.splitext(current_output)[0] + "_isolated" + os.path.splitext(current_output)[1]
            
            if is_video:
                # Extract audio from the CUT video
                temp_cut_audio = extract_audio(current_output)
                temp_isolated_audio = temp_cut_audio.replace(".mp3", "_iso.mp3")
                
                # Isolate
                isolate_audio(temp_cut_audio, eleven_key, temp_isolated_audio)
                
                # Merge back
                replace_audio_in_video(current_output, temp_isolated_audio, isolated_output)
                
                # Clean up temps
                if os.path.exists(temp_cut_audio): os.unlink(temp_cut_audio)
                if os.path.exists(temp_isolated_audio): os.unlink(temp_isolated_audio)
                
            else:
                # Direct audio isolation
                isolate_audio(current_output, eleven_key, isolated_output)
                
            current_output = isolated_output # Next step uses this output?
            
        # 5. Dub (Optional)
        if args.dub:
            # We dub the result of the previous step (cut or isolated)
            dub_output = os.path.splitext(current_output)[0] + f"_dubbed_{args.dub}" + os.path.splitext(current_output)[1]
            dub_media(current_output, args.dub, eleven_key, dub_output)
        
    finally:
        # Cleanup
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        if is_temp and os.path.exists(input_path):
            print("Cleaning up temporary input file...")
            os.unlink(input_path)
            if "tmp" in os.path.dirname(input_path): 
                 try:
                     os.rmdir(os.path.dirname(input_path))
                 except:
                     pass

if __name__ == "__main__":
    main()
