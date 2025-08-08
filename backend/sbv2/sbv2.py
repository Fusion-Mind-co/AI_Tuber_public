from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from pathlib import Path
from style_bert_vits2.tts_model import TTSModel
import sounddevice as sd
from flask import Blueprint, jsonify
from pathlib import Path

# Blueprintを作成（テスト用エンドポイントのため）
sbv2_bp = Blueprint('sbv2', __name__)

def sbv2_func(ai_message):
    print('sbv2_func関数実行！')
    print(f'音声変換するテキスト: {ai_message}')
    
    try:
        # ===============================日本語のモデルを使う(固定でOK)==============================
        bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
        bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

        # 現在のファイル（sbv2.py）の場所を基準に絶対パスを作成
        # flaskを使ってapp.pyから実行するときに、pathの現在地が変わってしまうため
        BASE_DIR = Path(__file__).resolve().parent

        #==============================モデルを読み込む=============================================
        model = TTSModel(
            model_path=str(BASE_DIR / "model/amitaro/amitaro.safetensors"),
            config_path=str(BASE_DIR / "model/amitaro/config.json"),
            style_vec_path=str(BASE_DIR / "model/amitaro/style_vectors.npy"),

            # cpu　か　cuda(gpu)を指定
            device="cuda",
        )

        # =========================================================================================

        # aiのメッセージを音声に変換
        sr, audio = model.infer(text=ai_message)

        #sounddeviceを使って音声再生
        print('音声再生を開始します...')
        sd.play(audio, sr)
        sd.wait()  # 再生完了まで待機
        print('音声再生が完了しました')

        return {"message": "音声再生完了", "status": "success"}
    
    except Exception as e:
        print(f'sbv2_func でエラーが発生: {e}')
        return {"message": f"音声再生エラー: {str(e)}", "status": "error"}
