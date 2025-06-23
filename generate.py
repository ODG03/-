import google.generativeai as genai
import time
import re
import os


# AIの設定
API_KEY = "AIzaSyBmfRaLY_reiBiIKD55fNgUoWXaFHhXxDc"
genai.configure(api_key=API_KEY)
model_ai = genai.GenerativeModel("gemini-2.0-flash")
#AIによる文生成
def generate_text(language):
    response = model_ai.generate_content(f"{language}の文を初心者向けに5個生成してください。日本語の説明は不要です。{language}の文章のみを出力してください。")
    sentences = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', response.text) if sentence.strip()]
    
    return sentences
  