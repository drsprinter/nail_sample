from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app, origins=["https://nsforb.web.fc2.com", "http://localhost:5500"])

# OpenAI クライアント初期化（APIキーは Render の環境変数に登録）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/makeup', methods=['POST', 'OPTIONS'])
def makeup():
    if request.method == 'OPTIONS':
        return '', 204  # CORS プリフライト応答

    data = request.get_json()
    prompt = data.get('prompt', '')

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはプロのメイクアップアーティストです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        plan = response.choices[0].message.content

        with open('latest_plan.txt', 'w', encoding='utf-8') as f:
            f.write(plan)

        return jsonify({'status': 'メイクプランの生成が完了しました。', 'plan': plan})

    except Exception as e:
        return jsonify({'status': 'エラーが発生しました', 'error': str(e)}), 500


@app.route('/')
def index():
    return result()  # トップページは最新のメイクプランを表示


@app.route('/result')
def result():
    try:
        with open('latest_plan.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return f'''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>あなたへのメイクプラン</title>
            <link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New&family=Zen+Antique+Soft&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Zen Kaku Gothic New', sans-serif;
                    background: #fdf8f5;
                    color: #4a3c38;
                    margin: 0;
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
                    color: #a8666e;
                    text-align: center;
                    margin-bottom: 1em;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-break: break-word;
                    background: #fff8f6;
                    padding: 1em;
                    border-left: 5px solid #f4cacc;
                    border-radius: 8px;
                    font-size: 1em;
                }}
                .image-container {{
                    text-align: center;
                    margin-top: 2em;
                }}
                .image-container img {{
                    width: 100%;
                    max-width: 400px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .caption {{
                    font-size: 0.9em;
                    color: #666;
                    margin-top: 0.5em;
                    text-align: center;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        padding: 1.2em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>あなたへのメイクプラン</h1>
                <pre>{content}</pre>
                <div class="image-container">
                    <img src="https://dummyimage.com/400x600/ffe8ed/000000&text=Makeup+Visual" alt="メイクイメージ画像">
                    <div class="caption">※この画像はメイクプランの参考イメージです</div>
                </div>
            </div>
        </body>
        </html>
        '''
    except FileNotFoundError:
        return '''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>メイクプラン未生成</title>
            <link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Zen Kaku Gothic New', sans-serif;
                    background: #fdf8f5;
                    color: #555;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    text-align: center;
                    padding: 2em;
                }}
                h1 {{
                    color: #a8666e;
                }}
            </style>
        </head>
        <body>
            <div>
                <h1>メイクプランはまだ生成されていません。</h1>
                <p>フォームから送信後に結果が表示されます。</p>
            </div>
        </body>
        </html>
        '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
