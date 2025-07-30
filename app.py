
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app, origins=["https://drsprinter.github.io",
    "https://drsprinter.github.io/nail_sample",
    "http://localhost:5500"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/makeup', methods=['POST', 'OPTIONS'])
def nail():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    try:
        # 質問項目を文字列に整形
        info = []
        for key, value in data.items():
            if isinstance(value, list):
                info.append(f"{key}: {', '.join(value)}")
            else:
                info.append(f"{key}: {value}")
        prompt = "\n".join(info)

        system_content = (
            "あなたはプロのネイリストです。"
            "以下のお客様情報をもとに、ネイルプランを生成してください。"
            "出力は次の2つのセクションに分けてください：\n"
            "[お客様向けネイルコンセプト]：感性に響く丁寧な説明、使用カラーやイメージなど。\n"
            "[サロン向け技術メモ]：プリジェル顔料を使ったカラー調合比率、使用カラー名、塗布順、ポイントなど。"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        plan = response.choices[0].message.content

        with open('latest_plan.txt', 'w', encoding='utf-8') as f:
            f.write(plan)

        return jsonify({'status': 'ネイルプランの生成が完了しました。', 'plan': plan})

    except Exception as e:
        return jsonify({'status': 'エラーが発生しました', 'error': str(e)}), 500


@app.route('/')
def index():
    return redirect("/result")


@app.route('/result')
def result():
    try:
        with open('latest_plan.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return f"""
        <!DOCTYPE html>
        <html lang='ja'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>ネイルカウンセリング結果</title>
            <link href='https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New&family=Zen+Antique+Soft&display=swap' rel='stylesheet'>
            <style>
                body {{
                    font-family: 'Zen Kaku Gothic New', sans-serif;
                    background: #fff9f6;
                    color: #3c2f2f;
                    padding: 1em;
                    line-height: 1.7;
                }}
                .container {{
                    max-width: 720px;
                    margin: auto;
                    background: #ffffff;
                    padding: 2em;
                    border-radius: 16px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                }}
                h1 {{
                    font-family: 'Zen Antique Soft', serif;
                    font-size: 1.8em;
                    color: #d08874;
                    text-align: center;
                }}
                pre {{
                    white-space: pre-wrap;
                    background: #fef6f2;
                    padding: 1em;
                    border-left: 5px solid #f4cacc;
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <div class='container'>
                <h1>あなたへのネイルプラン</h1>
                <pre>{content}</pre>
            </div>
        </body>
        </html>
        """
    except FileNotFoundError:
        return "<h2>ネイルプランはまだ生成されていません。</h2>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
