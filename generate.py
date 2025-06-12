from flask import Flask, render_template, request
import pyaudio
import wave
import whisper
import google.generativeai as genai
import pandas as pd
import time
import re
import os
from rapidfuzz import fuzz

# AIの設定
API_KEY = "AIzaSyDRaStCE57-Z67lzx6mNFpYNlDDyuwP9J4"
genai.configure(api_key=API_KEY)
model_ai = genai.GenerativeModel("gemini-2.0-flash")
#AIによる文生成
def generate_text(language):
    response = model_ai.generate_content(f"{language}の文を初心者向けに5個生成してください。日本語の説明は不要です。{language}の文章のみを出力してください。")
    sentences = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', response.text) if sentence.strip()]
    
    return sentences
  