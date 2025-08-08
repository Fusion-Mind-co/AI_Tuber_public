# news_selector.py
from flask import Blueprint, jsonify, request
import json
import os
from llm_chat import gemini_func, ollama_func

news_selector_bp = Blueprint('news_selector', __name__)

def select_best_news(news_data, ai_personality, provider, llm_model):
    """LLMを使ってニュースを厳選"""
    try:
        # 1. 全ニュースをテキスト形式に変換
        news_list = []
        all_news_objects = []  # 後で特定するためのオブジェクト保存
        
        category_names = {
            'anime_game': 'アニメ・ゲーム',
            'tech': 'テック・IT',
            'weather': '天気・災害'
        }
        
        for category, items in news_data['categories'].items():
            for i, item in enumerate(items):
                news_text = f"【{category_names.get(category, category)}】タイトル: {item['title']}\n概要: {item['description']}"
                news_list.append(news_text)
                all_news_objects.append(item)  # 対応するオブジェクトを保存
        
        print(f"📝 厳選対象ニュース数: {len(news_list)}件")
        
        # 2. 厳選プロンプト作成
        prompt = f"""以下のニュース一覧から、AIVtuber（性格: {ai_personality}）の話題作りに最適なニュースを1つ選んでください。

YouTubeでの配信で視聴者が興味を持ちやすく、キャラクターの性格に合ったニュースを選択してください。

=== ニュース一覧 ===
{chr(10).join(news_list)}

選択したニュースのタイトル部分をそのまま正確に回答してください（「タイトル: 」は除く）。
"""
        
        print("🤖 LLMでニュース厳選中...")
        
        # 3. 既存LLM関数で選択
        character = "ニュース選定の専門家として、AIVtuberの配信に最適なニュースを客観的に判断する"
        
        if provider == 'gemini':
            selected_title = gemini_func(prompt, llm_model, character)
        elif provider == 'ollama':
            selected_title = ollama_func(prompt, llm_model, character)
        else:
            raise ValueError(f"未対応のプロバイダー: {provider}")
        
        print(f"🎯 LLMが選択したタイトル: {selected_title}")
        
        # 4. タイトルから実際のニュースオブジェクトを特定
        selected_title_clean = selected_title.strip()
        
        for news_obj in all_news_objects:
            if selected_title_clean in news_obj['title'] or news_obj['title'] in selected_title_clean:
                print(f"✅ 一致するニュースを発見: {news_obj['title']}")
                return news_obj
        
        # 見つからない場合は最初のニュースを返す（フォールバック）
        print("⚠️ タイトル一致するニュースが見つからないため、最初のニュースを選択")
        return all_news_objects[0] if all_news_objects else None
        
    except Exception as e:
        print(f"❌ ニュース厳選エラー: {str(e)}")
        return None

@news_selector_bp.route('/api/news/select', methods=['POST'])
def select_news_api():
    """ニュース厳選API"""
    try:
        # リクエストからパラメータ取得
        data = request.get_json()
        ai_personality = data.get('ai_personality', '明るくて元気で親しみやすい女の子')
        provider = data.get('provider', 'gemini')
        llm_model = data.get('llm_model', 'gemini-2.0-flash-exp')
        
        print(f"🎯 ニュース厳選開始 - AI性格: {ai_personality}")
        
        # 現在のニュースデータを読み込み
        if not os.path.exists('static/news.json'):
            return jsonify({'error': 'ニュースデータが見つかりません。先にニュースを取得してください。'}), 404
        
        with open('static/news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # ニュースが空でないかチェック
        total_news = sum(len(items) for items in news_data['categories'].values())
        if total_news == 0:
            return jsonify({'error': 'ニュースデータが空です。'}), 400
        
        # LLMでニュース厳選
        selected_news = select_best_news(news_data, ai_personality, provider, llm_model)
        
        if selected_news:
            return jsonify({
                'message': 'ニュース厳選完了',
                'selected_news': selected_news,
                'total_news_count': total_news,
                'success': True
            })
        else:
            return jsonify({'error': 'ニュース厳選に失敗しました'}), 500
            
    except Exception as e:
        print(f"❌ API エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500