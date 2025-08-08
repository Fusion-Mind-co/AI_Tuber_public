import pytchat
import json

# YouTube Live の動画IDを指定
video_id = "ここにID入力"

# pytchat のライブチャットオブジェクトを作成
chat = pytchat.create(video_id)

# JSON ファイルを開く
chat_data = []

# チャットが生きている間コメントを取得
while chat.is_alive():
    for c in chat.get().items:
        chat_data.append({
            "timestamp": c.datetime,
            "username": c.author.name,
            "message": c.message,
            "amount": c.amountValue,
            "currency": c.currency,
        })
        print(f"[{c.datetime}] {c.author.name}: {c.message}")  # ターミナルにも表示

    # 定期的に JSON ファイルに保存
    with open("chat_log.json", "w", encoding="utf-8") as file:
        json.dump(chat_data, file, ensure_ascii=False, indent=4)
        