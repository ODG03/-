from flask import Flask, render_template, request
import generate
import listen
import pandas as pd
import secrets
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # セッションなしだが安全性確保

results_list = []  # 全ての評価結果を保持するリスト
sentences_list = []  # 生成された文リストを保持

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/trans", methods=["POST"])
def trans():
    global sentences_list, results_list
    
    language = request.form["language"]
    choice = request.form["choice"]
    record_time = int(request.form["record_time"])
    index = int(request.form.get("index", 0))

    raw_text = request.form.get("raw_text", "").strip()  # 🔹 入力されたテキストを取得

    if index == 0:
        results_list = []  # 🔹 初回リクエスト時に結果をリセット

    if choice == "Yes":
        sentences_list = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', raw_text) if sentence.strip()]
    else:
        sentences_list = generate.generate_text(language)

    num = len(sentences_list)

    if index < num:
        result = listen.listen_evaluate(sentences_list[index], language, record_time)
        results_list.append(result.to_dict(orient="records")[0])

        df_html = result.to_html(classes="horizontal-table", index=False)

        return render_template("trans.html", sentence=sentences_list[index], df_html=df_html, index=index, num=num, language=language, record_time=record_time, raw_text=raw_text)
    
    return result_page(language)


def result_page(language):
    """🔹 `result()` の処理を関数化して `trans()` からも呼び出せるようにする"""
    df_final = pd.DataFrame(results_list)
    df_html = df_final.to_html(classes="horizontal-table", index=False)

    # Gemini AI に発音評価データを渡して分析してもらう
    analysis_prompt = f"""
    以下の発音評価データから、ユーザーの発音の弱点を指摘し、改善のアドバイスをしてください。

    {df_final.to_string()}
    
    日本語で簡潔に講評をお願いします。
    """
    
    analysis = generate.model_ai.generate_content(analysis_prompt).text  # 🔹 AI に講評生成を依頼

    return render_template("result.html", language=language, df_html=df_html, analysis=analysis)

@app.route("/result", methods=["POST"])
def result():
    language = request.form.get("language", "英語")  # 言語を適切に管理
    return result_page(language)

@app.route("/retry", methods=["POST"])
def retry():
    global results_list, sentences_list
    results_list = []  # 結果リストをリセット
    sentences_list = []  # 文リストをリセット
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)