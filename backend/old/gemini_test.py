# gemini ライブラリのインポート
import google.generativeai as gemini
from flask import Blueprint, jsonify

# .envファイルからコードを読み取るライブラリ
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()



# Blueprintを作成
gemini_test_bp = Blueprint('gemini_test', __name__)

# ルートを定義
@gemini_test_bp.route('/api/gemini/test')

def gemini_test_func():
    print('gemini()関数')

    # ===========================API KEYを設定===============================

    # .envからapi keyを取得
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    # APIキーを設定
    gemini.configure(api_key=gemini_api_key)


    # ===========================modelを設定===============================
    # modelを設定
    model = gemini.GenerativeModel('gemini-2.0-flash-exp')


    # ===========================プロンプトを入力===============================
    # プロンプト(ユーザーが投げかける文章)
    prompt = "こんにちは"


    # ============geminiにpromptを送信し結果をresponseに返す=====================
    response = model.generate_content(prompt)
    
    
    print(response.text)

    return jsonify({"message": response.text})

# 関数を呼び出す
if __name__ == "__main__":
    gemini_test_func()