import pyaudio
import wave
import whisper
import pandas as pd
import os
from rapidfuzz import fuzz

# 録音の設定（初期値）
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "output.wav"

# Whisperモデルのロード
model_listen = whisper.load_model("large")

# 録音＆評価処理
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

    # 無音チェック
    if os.path.getsize(OUTPUT_FILENAME) < 1000:  # 🔹 無音ファイルの判定
        return pd.DataFrame([{"AIの文": sentence, "あなたの発音": "（無音）", "類似度スコア": 0}])

    # 言語設定
    lang = "ko" if foreign_lang == "韓国語" else "en"


    # Whisperで文字起こし（エラーハンドリングを追加）
    try:
        voice = model_listen.transcribe(OUTPUT_FILENAME, language=lang)
        print(voice)
        user_sentence = voice["text"].strip()
        # 🔹 無音やノイズをチェック
        if not user_sentence or user_sentence.lower() in ["", "um", "uh", "hmm"]:
            user_sentence = "（雑音のみ検出）"

    except RuntimeError:
        print(f"ERROR: Whisperの文字起こし失敗 → {str(e)}")
        user_sentence = "（音声の解析に失敗）"
        return pd.DataFrame([{"AIの文": sentence, "あなたの発音": "（音声の解析に失敗）", "類似度スコア": 0}])

    # 類似度評価
    similarity = fuzz.ratio(sentence, user_sentence)
    if similarity < 30:
        user_sentence = "（認識に失敗しました）"
        similarity = 0
    print("DEBUG: 録音ファイルのサイズ =", os.path.getsize("output.wav"))
    print("DEBUG: Whisperの文字起こし結果 =", voice["text"].strip())
    print("DEBUG: Whisperの設定言語 =", lang) 
    return pd.DataFrame([{"AIの文": sentence, "あなたの発音": user_sentence, "類似度スコア": similarity}])
