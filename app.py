from flask import Flask, render_template, request
import pyaudio
import wave
import whisper
import google.generativeai as genai
import pandas as pd
import time
import re
from rapidfuzz import fuzz

app = Flask(__name__)

# AIの設定
API_KEY = "AIzaSyDRaStCE57-Z67lzx6mNFpYNlDDyuwP9J4"
genai.configure(api_key=API_KEY)
model_ai = genai.GenerativeModel("gemini-2.0-flash")
model_listen = whisper.load_model("medium")

# 録音の設定（初期値）
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "output.wav"

#AIによる文生成
def generate_text(language):
    response = model_ai.generate_content(f"{language}の文を初心者向けに5個生成してください。日本語の説明は不要です。{language}の文章のみを出力してください。")
    sentences = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', response.text) if sentence.strip()]
    
    return sentences

#外国語選択と録音時間の入力から録音して類似度を返す(1個の文について評価)
def listen_evaluate(sentence,foreign_lang,record_time):
    result = []
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    for _ in range(0, int(RATE / CHUNK * record_time)):  
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 音声ファイル保存
    waveFile = wave.open(OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    if foreign_lang == "韓国語":
        lang = "ko"
    else:
        lang = "en"

    # Whisperで文字起こし
    voice = model_listen.transcribe(OUTPUT_FILENAME, language=lang)
    user_sentence = voice["text"].strip()

        
    # AIの文と比較
    similarity = fuzz.ratio(sentence, user_sentence)   # 類似度計算
    result.append({"AIの文": sentence, "あなたの発音": user_sentence, "類似度スコア": similarity})
    df = pd.DataFrame(result, columns=["AIの文", "あなたの発音", "類似度スコア"])
    df.index = range(1, len(df)+1)  # インデックスを 1 から開始
    return df
        
       

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/trans", methods=["POST"])
def trans():
    language = request.form["language"]
    choice = request.form["choice"]
    record_time = int(request.form["record_time"])
    
    
    try:
        index = int(request.form["index"])
    
    except:
        index = 0
    

    if choice == "Yes":
        raw_text = request.form["raw_text"]
        sentences = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', raw_text) if sentence.strip()]
    
    else:
        sentences = generate_text(language)

    num = len(sentences)
    
    for sentence in sentences:
        df = listen_evaluate(sentence,language,record_time)
        df_html = df.to_html(classes="horizontal-table", index=False)

    return render_template("trans.html",sentence=sentences[index],df_html=df_html,index=index)




@app.route("/retry", methods=["POST"])
def retry():
    language = request.form["language"]
    raw_text = generate_text(language)
    return render_template("check.html", language=language, sentences=raw_text.split("\n"), index=0)

if __name__ == "__main__":
    app.run(debug=True)