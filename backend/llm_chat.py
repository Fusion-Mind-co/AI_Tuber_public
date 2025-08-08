# flask
from flask import Blueprint, jsonify, request

# gemini
import google.generativeai as gemini

# ollama
from ollama import chat , ChatResponse

# sbv2の音声合成機能をインポート
from sbv2.sbv2 import sbv2_func

# .envファイル
from dotenv import load_dotenv
import os


# .envファイルを読み込む
load_dotenv()

# Blueprintを作成
llm_chat_bp = Blueprint('llm_chat', __name__)

# ルートを定義（POSTメソッドを追加）
@llm_chat_bp.route('/api/llmchat', methods=['POST'])
def llm_chat():
    print('llmchat()関数')

    try:
        
        # フロントエンドからJSONデータを取得　受け取るデータは4つ
        request_data = request.get_json()
        
        # メッセージが空だったらエラーを返す
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





        # これから設定！！！！！！！！！！！！！！！！！！！

        # LLMの種類
        provider = request_data.get('provider')
        print('provider =', provider)

        # LLMのモデル
        llm_model = request_data.get('llm_model')
        print('llm_model =', llm_model)




        # これから設定！！！！！！！！！！！！！！！！！！！






        # ==========　【キャラ設定】　名前と性格　===========
        character = f"""
        
        あなたの名前:{ai_name}
        性格設定：{ai_personality}
        上記の名前と性格設定に従って、一貫性を持って返答
        会話ベースであり、要求されない限り解説や説明は控える
        
        """


        # providerの中身に応じて対応したLLM関数を呼び出す
        if provider == 'gemini':
            response = gemini_func(user_message,llm_model,character)

        elif provider == 'ollama':
            response = ollama_func(user_message,llm_model,character)





        # ============sbv2で音声出力=====================
        try:
            print('sbv2_func()を呼び出します...')
            # sbv2_func にGeminiの回答テキストを渡して音声出力
            sbv2_func(response)
            print('音声出力が完了しました')
        except Exception as voice_error:
            print(f"音声出力エラー: {voice_error}")
            # 音声出力エラーが発生してもテキスト回答は返す

        return jsonify({
            "message": response,
            "ai_name": ai_name
        })
        # ===============================================
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return jsonify({"error": "サーバーエラーが発生しました"}), 500




# 【gemini】||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

def gemini_func(user_message,llm_model,character):
    print('gemini()関数')

    # ===========================API KEYを設定===============================

    # .envからapi keyを取得
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    # APIキーを設定
    gemini.configure(api_key=gemini_api_key)


    # ===========================モデルとキャラクターを設定===============================
    model = gemini.GenerativeModel(
        llm_model,
        system_instruction=character
    )


    # ============geminiにpromptを送信し結果をresponseに返す=====================
    response = model.generate_content(user_message)
    
    print(f"Geminiレスポンス: {response.text}")

    # テキストのみを返す（jsonifyは呼び出し元で行う）
    return response.text


# 【ollama】||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

def ollama_func(user_message,llm_model,character):
    
    response: ChatResponse = chat(model=llm_model, messages=[
    {
        'role': 'system',
        'content': character
    },
    {
        'role': 'user',
        'content': user_message
    },
    ])

    return response.message.content