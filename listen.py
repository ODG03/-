from flask import Flask, render_template, request
import pyaudio
import wave
import whisper
import google.generativeai as genai
import pandas as pd
import time
import re
from rapidfuzz import fuzz
 # 録音の設定（初期値）
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "output.wav"
result = []
audio = pyaudio.PyAudio()
model_listen = whisper.load_model("medium")

#外国語選択と録音時間の入力から録音して類似度を返す(1個の文について評価)
def listen_evaluate(sentence, foreign_lang, record_time):
    # 録音処理
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

    lang = "ko" if foreign_lang == "韓国語" else "en"

    # Whisperで文字起こし
    voice = model_listen.transcribe(OUTPUT_FILENAME, language=lang)
    user_sentence = voice["text"].strip()

    # 🔹 録音データが空ならエラーメッセージを返す
    if not user_sentence:
        return {"AIの文": sentence, "あなたの発音": "録音が検出されませんでした", "類似度スコア": 0}

    similarity = fuzz.ratio(sentence, user_sentence)  # 類似度計算

    return {"AIの文": sentence, "あなたの発音": user_sentence, "類似度スコア": similarity}
