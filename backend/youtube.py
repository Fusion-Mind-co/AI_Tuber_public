# flask
from flask import Blueprint, jsonify, request
import threading
import time

# youtubeからコメント取得
import pytchat

# json
import json
import os

# Blueprintを作成
youtube_bp = Blueprint('youtube', __name__)

# グローバル変数でチャット状態を管理
active_chats = {}

def collect_comments(video_id, max_duration=300):  # 最大5分
    """バックグラウンドでコメントを収集する関数"""
    try:
        # pytchatをバックグラウンドで安全に実行するための設定
        import signal
        signal.signal = lambda signum, handler: None  # signalを無効化
        
        chat = pytchat.create(video_id)
        chat_data = []
        start_time = time.time()
        
        while chat.is_alive():
            # 最大時間をチェック
            if time.time() - start_time > max_duration:
                print(f"最大収集時間（{max_duration}秒）に達しました")
                break
            
            # active_chatsから削除された場合は停止
            if video_id not in active_chats:
                print(f"video_id: {video_id} のコメント収集が停止されました")
                break
                
            try:
                for c in chat.get().items:
                    chat_data.append({
                        "timestamp": c.datetime,
                        "username": c.author.name,
                        "message": c.message,
                        "amount": c.amountValue if hasattr(c, 'amountValue') else 0,
                        "currency": c.currency if hasattr(c, 'currency') else "",
                    })
                    print(f"[{c.datetime}] {c.author.name}: {c.message}")
                
                # 定期的にファイル保存
                if chat_data:
                    filename = f"chat_log_{video_id}.json"
                    with open(filename, "w", encoding="utf-8") as file:
                        json.dump(chat_data, file, ensure_ascii=False, indent=4)
                        
            except Exception as inner_e:
                print(f"コメント取得中のエラー: {inner_e}")
                continue
            
            # 少し待機してCPU負荷を軽減
            time.sleep(2)
            
    except Exception as e:
        print(f"コメント収集エラー: {e}")
    finally:
        # アクティブチャットから削除
        if video_id in active_chats:
            del active_chats[video_id]
            print(f"video_id: {video_id} のコメント収集を終了しました")

@youtube_bp.route('/api/youtube', methods=['POST'])
def youtube_comment():
    try:
        # フロントエンドからJSONデータを取得
        request_data = request.get_json()
        
        if not request_data or 'video_id' not in request_data:
            return jsonify({'error': 'video_id が必要です'}), 400
            
        video_id = request_data['video_id']
        
        # video_idの基本的なバリデーション（YouTubeのIDは11文字）
        if len(video_id) != 11:
            return jsonify({'error': '無効なvideo_idです（11文字である必要があります）'}), 400
        
        # 既に収集中かチェック
        if video_id in active_chats:
            return jsonify({'message': 'このビデオのコメント収集は既に実行中です'}), 200
        
        # バックグラウンドでコメント収集を開始
        active_chats[video_id] = True
        thread = threading.Thread(target=collect_comments, args=(video_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'コメント収集を開始しました',
            'video_id': video_id,
            'status': 'started'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500

@youtube_bp.route('/api/youtube/status/<video_id>', methods=['GET'])
def youtube_status(video_id):
    """コメント収集の状態をチェックする新しいエンドポイント"""
    is_active = video_id in active_chats
    
    # ファイルの存在確認
    filename = f"chat_log_{video_id}.json"
    file_exists = os.path.exists(filename)
    
    comment_count = 0
    if file_exists:
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                comment_count = len(data)
        except:
            pass
    
    return jsonify({
        'video_id': video_id,
        'is_collecting': is_active,
        'file_exists': file_exists,
        'comment_count': comment_count
    })

@youtube_bp.route('/api/youtube/stop/<video_id>', methods=['POST'])
def stop_youtube_comment(video_id):
    """コメント収集を停止する新しいエンドポイント"""
    if video_id in active_chats:
        del active_chats[video_id]
        return jsonify({'message': f'video_id: {video_id} のコメント収集を停止しました'})
    else:
        return jsonify({'message': 'このビデオのコメント収集は実行されていません'}), 404