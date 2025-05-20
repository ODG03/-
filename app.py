import pyaudio
import wave
import whisper
import google.generativeai as genai
import difflib
from difflib import SequenceMatcher
from rapidfuzz import fuzz
import time
import re
import pandas as pd
import numpy as np


API_KEY = "AIzaSyDRaStCE57-Z67lzx6mNFpYNlDDyuwP9J4"
genai.configure(api_key=API_KEY)
choice = input("自分の文章を使いますか？ [Yes or No] :")
foreign_lang = input("何語をチェックしますか？ [韓国語 or 英語] :")
def get_foreign_example(foreign_lang):
    model_ai = genai.GenerativeModel("gemini-2.0-flash")
    response = model_ai.generate_content(f"{foreign_lang}の簡単な文をいくつか生成してください.日本語の説明は不要です。{foreign_lang}の文章のみを出力してください。")
    return response.text

if choice=="Yes":
    raw_text = input("\n文章を入力してください:")

else:
    # AIから韓国語の例文を取得
    raw_text = get_foreign_example(foreign_lang)


# 文単位で分割（「.」「?」「!」で区切る）
foreign_sentences = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', raw_text) if sentence.strip()]
model_listen = whisper.load_model("medium")

# 録音の設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 8  # 各文の録音時間
OUTPUT_FILENAME = "output.wav"

#結果の表示
results = []

# 各文ごとに音読＆比較
for index, sentence in enumerate(foreign_sentences):
    print(f"\n🔊 {index+1}番目の文を音読してください: {sentence}")

    # 録音開始の表示（強調）
    print("🎤 録音開始...")
    
    # 録音開始
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):  # 指定時間録音
        data = stream.read(CHUNK)
        frames.append(data)

    print("✅ 録音終了")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 音声ファイルを保存
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
    result = model_listen.transcribe(OUTPUT_FILENAME, language=lang)
    user_sentence = result["text"].strip()

    # Whisperの出力を確認
    print(f"\n【Whisperの出力】 {user_sentence}")

    # AIの文と比較
    similarity = fuzz.ratio(sentence, user_sentence)   # 類似度計算

    results.append({"AIの文": sentence, "あなたの発音": user_sentence, "類似度スコア": similarity})
    
    print(f"\n【AIの文】 {sentence}")
    print(f"【あなたの発音】 {user_sentence}")
    print(f"✅ 類似度スコア: {similarity:.2f}")

    # 次の文に進む前に少し待機
    time.sleep(1)

#データフレームにして表示
df = pd.DataFrame(results)
df_text = df.to_string()
print("\n 発音チェック\n")
print(df)
model_ai = genai.GenerativeModel("gemini-2.0-flash")
res = model_ai.generate_content(f"以上の発音チェック結果を分析して、どこの発音が弱点かを指摘してください\n\n{df_text}")

print("\n📊 発音の弱点分析\n")
print(res.text)