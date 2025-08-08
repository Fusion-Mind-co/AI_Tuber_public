# gemini ライブラリのインポート
import google.generativeai as gemini
from flask import Blueprint, jsonify, request

# .envファイルからコードを読み取るライブラリ
from dotenv import load_dotenv
import os

# sbv2の音声合成機能をインポート
from sbv2.sbv2 import sbv2_func

# .envファイルを読み込む
load_dotenv()

# Blueprintを作成
gemini_bp = Blueprint('gemini', __name__)

# ルートを定義（POSTメソッドを追加）
@gemini_bp.route('/api/gemini', methods=['POST'])
def gemini_func():
    print('gemini()関数')

    try:
        # ===========================API KEYを設定===============================
        # .envからapi keyを取得
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_api_key:
            return jsonify({"error": "API キーが設定されていません"}), 500
        
        # APIキーを設定
        gemini.configure(api_key=gemini_api_key)

        # ===========================プロンプトを入力===============================
        # リクエストボディからJSONデータを取得
        request_data = request.get_json()
        
        if not request_data or 'message' not in request_data:
            return jsonify({"error": "メッセージが含まれていません"}), 400
        
        # メッセージ(プロンプト)
        user_message = request_data.get('message')
        print('user_message =', user_message)

        # AIの名前
        ai_name = request_data.get('aiName')
        print('ai_name =', ai_name)

        # キャラ付け
        ai_personality = request_data.get('aiPersonality')
        print('ai_personality =', ai_personality)

        if not user_message or not user_message.strip():
            return jsonify({"error": "空のメッセージです"}), 400
        

        # ==========system_instruction = 名前の設定と性格付け===========
        character = f"""
        
        あなたの名前:{ai_name}
        性格設定：{ai_personality}
        上記の名前と性格設定に従って、一貫性を持って返答
        自分の名前を聞かれた時は「{ai_name}」と答える
        会話ベースであり、要求されない限り解説や説明は控える
        
        """

        # ===========================modelを設定===============================
        model = gemini.GenerativeModel(
            'gemini-2.0-flash-exp',
            system_instruction=character
        )
        
        # 新しいチャットセッションを開始（履歴なし）
        chat = model.start_chat(history=[])

        # ============geminiにメッセージを送信=====================
        response = chat.send_message(user_message)
        
        print('response.text =', response.text)

        # ============sbv2で音声出力=====================
        try:
            print('sbv2_func()を呼び出します...')
            # sbv2_func にGeminiの回答テキストを渡して音声出力
            sbv2_result = sbv2_func(response.text)
            print('音声出力が完了しました')
        except Exception as voice_error:
            print(f"音声出力エラー: {voice_error}")
            # 音声出力エラーが発生してもテキスト回答は返す

        return jsonify({
            "message": response.text,
            "ai_name": ai_name
        })
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return jsonify({"error": "サーバーエラーが発生しました"}), 500

# 関数を呼び出す
if __name__ == "__main__":
    gemini_func()