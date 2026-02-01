import os
import sys
import json
import google.oauth2.credentials
import google.auth.transport.requests
from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2
from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2_grpc
import grpc

# Force pure Python implementation for protobuf
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

def main():
    if len(sys.argv) < 2:
        print("Usage: python control.py 'your command'")
        return

    query = sys.argv[1]
    
    # Check for credentials in standard locations
    # 1. Environment variable GOG_HOME_CREDS
    # 2. Local config folder ~/.config/google-oauthlib-tool/credentials.json
    creds_path = os.environ.get('GOG_HOME_CREDS')
    if not creds_path:
        creds_path = os.path.expanduser('~/.config/google-oauthlib-tool/credentials.json')

    if not os.path.exists(creds_path):
        print(f"Error: Credentials not found at {creds_path}")
        print("Please set GOG_HOME_CREDS environment variable or place credentials.json in ~/.config/google-oauthlib-tool/")
        return

    with open(creds_path, 'r') as f:
        creds_data = json.load(f)

    credentials = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes']
    )

    request = google.auth.transport.requests.Request()
    credentials.refresh(request)

    grpc_channel = grpc.secure_channel('embeddedassistant.googleapis.com', grpc.ssl_channel_credentials())
    assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(grpc_channel)

    config = embedded_assistant_pb2.AssistConfig(
        text_query=query,
        device_config=embedded_assistant_pb2.DeviceConfig(
            device_id='openclaw_agent',
            device_model_id='openclaw_agent_model'
        ),
    )

    config.audio_out_config.encoding = embedded_assistant_pb2.AudioOutConfig.LINEAR16
    config.audio_out_config.sample_rate_hertz = 16000
    config.audio_out_config.volume_percentage = 0

    def generate_requests():
        yield embedded_assistant_pb2.AssistRequest(config=config)

    responses = assistant.Assist(generate_requests(), metadata=[('authorization', 'Bearer ' + credentials.token)])
    
    try:
        for resp in responses:
            if resp.dialog_state_out.supplemental_display_text:
                print(f"Response: {resp.dialog_state_out.supplemental_display_text}")
            if resp.device_action.device_request_json:
                print(f"Action: {resp.device_action.device_request_json}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
