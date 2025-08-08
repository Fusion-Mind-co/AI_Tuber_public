from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from pathlib import Path
from style_bert_vits2.tts_model import TTSModel
import sounddevice as sd
from flask import Blueprint, jsonify
from pathlib import Path

# Blueprintを作成
sbv2_test_bp = Blueprint('sbv2_test', __name__)

# ルートを定義
@sbv2_test_bp.route('/api/sbv2/test')

def sbv2_test_func():
    print('sbv2_func関数実行！')
    # ===============================日本語のモデルを使う(固定でOK)==============================
    bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
    bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

    # ↑ほかの選択肢
    # "cl-tohoku/bert-base-japanese-v3"
    # "rinna/japanese-roberta-base"

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

    #「こんにちは」と発話
    sr, audio = model.infer(text="こんにちは")

    #sounddeviceを使って音声再生
    sd.play(audio, sr)
    sd.wait()

    return jsonify({"message": "音声再生完了"})


if __name__ == "__main__": 
    sbv2_test_func()