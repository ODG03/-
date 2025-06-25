from flask import Flask, render_template, request
import generate
import listen
import pandas as pd
import secrets
from flask import Flask, render_template, request
import generate
import listen
import pandas as pd
import secrets
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

results_list = []
sentences_list = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/trans", methods=["POST"])
def trans():
    global sentences_list, results_list
    
    language = request.form["language"]
    choice = request.form.get("choice", "No")  # 🔹 KeyError対策
    record_time = int(request.form["record_time"])
    index = int(request.form.get("index", -1))

    raw_text = request.form.get("raw_text", "").strip()

    if index == -1:
        results_list = []
        if choice == "Yes":
            if not raw_text:
                return render_template("trans.html", error="エラー: テキストを入力してください！", raw_text=raw_text)
            sentences_list = [sentence.strip() for sentence in re.split(r'\s*[.?!]\s*', raw_text) if sentence.strip()]
        else:
            sentences_list = generate.generate_text(language)
    print(sentences_list)

    num = len(sentences_list)

    if index == -1:
        index = 0
        return render_template("trans.html",sentence=sentences_list[index], index=index, num=num, language=language, record_time=record_time, raw_text=raw_text)

    if index < num:
        result_df = listen.listen_evaluate(sentences_list[index], language, record_time)
        results_list.append(result_df.iloc[0].to_dict())  # 1行分をdictでappend

        df_html = result_df.to_html(classes="horizontal-table", index=False)

        return render_template("trans.html", sentence=sentences_list[index], df_html=df_html, index=index, num=num, language=language, record_time=record_time, raw_text=raw_text)
    
    return result_page(language)

@app.route("/result", methods=["POST"])
def result():
    language = request.form.get("language", "英語")
    return result_page(language)

def result_page(language):
    df_final = pd.DataFrame(results_list)
    df_html = df_final.to_html(classes="horizontal-table", index=False)

    analysis_prompt = f"""
    以下の発音評価データから、ユーザーの発音の弱点を指摘し、改善のアドバイスをしてください。

    {df_final.to_string()}
    
    日本語で簡潔に講評をお願いします。
    """
    
    analysis = generate.model_ai.generate_content(analysis_prompt).text

    return render_template("result.html", language=language, df_html=df_html, analysis=analysis)

@app.route("/next", methods=["POST"])
def next():
    global sentences_list, results_list
    language = request.form["language"]
    record_time = int(request.form["record_time"])
    index = int(request.form.get("index", -1))
    num = len(sentences_list)
    return render_template("trans.html", sentence=sentences_list[index],index=index, language=language, record_time=record_time,num=num)
    

@app.route("/retry", methods=["POST"])
def retry():
    global results_list, sentences_list
    results_list = []
    sentences_list = []
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)