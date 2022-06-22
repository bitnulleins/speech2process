import os
import json

from flask import Flask, render_template, request, redirect, jsonify
from speech_to_process import Speech2Process

app = Flask(__name__)
AUDIO_DIR = './audio'

def get_audio_files():
    return [ f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav") ]

@app.route("/process/create", methods=['POST'])
def form():
    body_request_type = request.args.get('body_request_type','audio')
    processor = Speech2Process()

    if body_request_type == 'audio':
        # Save all new steps as file
        for file in request.files.getlist('file'):
            with open(os.path.abspath(f'{AUDIO_DIR}/{file.filename}.wav'), 'wb') as f:
                f.write(file.read())

        response = jsonify(processor.from_audio(get_audio_files()))
    else:
        text = json.loads(request.data)
        response = jsonify(processor.from_text(text))
        
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/", methods=["GET"])
def index():
    # Remove all old files
    for f in get_audio_files(): os.remove(os.path.join(AUDIO_DIR, f))
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)