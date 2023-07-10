import os
import subprocess

import openai
import yt_dlp
from dotenv import load_dotenv
from flask import Flask, jsonify, request

app = Flask(__name__)

load_dotenv()

openai.api_key = os.getenv('API_KEY')
openai.organization = os.getenv('ORGANIZATION')



@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    # Get the YouTube video URL from the request
    youtube_url = request.json['youtube_url']
    question = request.json['question']

    # Download the audio from the YouTube video
    audio_filename = download_audio(youtube_url)

    # Transcribe the audio using Whisper ASR
    transcript = transcribe_audio(audio_filename)

    # Return the transcript as the API response
    chatgpt = question_audio(transcript, question)
    return jsonify({
        'transcript': transcript,
        'response': chatgpt
    })

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return 'audio.wav'

def transcribe_audio(audio_filename):
    subprocess.run(['python', '-m', 'whisper', audio_filename], check=True) #  '--model', 'base.en', 
    with open('audio.txt', 'r') as f:
        transcript = f.read()

    return transcript


def question_audio(transcript, question):
    # Concatenate the question and text data
    input_text = question + '\n' + transcript

    # Generate a response using OpenAI's GPT model
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": input_text}
        ]
    )

    print(completion)
    return completion.choices[0].message.content


if __name__ == '__main__':
    app.run(debug=True)





# curl -X POST -H "Content-Type: application/json" -d "{\"youtube_url\":\"https://www.youtube.com/watch?v=pXe_Wt-Qu4E\", \"question\":\"Summarise how to create a sandwich from the following text.\"}" "http://localhost:5000/transcribe"


"""
curl -X POST -H "Content-Type: application/json" -d '{
    "youtube_url": "https://www.youtube.com/watch?v=pXe_Wt-Qu4E",
    "question": "Summarise how to create a sandwich from the following text"
}' http://localhost:5000/transcribe

"""