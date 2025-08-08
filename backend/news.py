# news.py
from flask import Blueprint, jsonify
import feedparser
import requests
import json
import os
from datetime import datetime
import re

news_bp = Blueprint('news', __name__)

@news_bp.route('/api/news/refresh', methods=['POST'])
def get_news():
    """ニュース取得・保存・返却を全て実行（Flask APIエンドポイント兼用）"""
    try:
        print("📡 ニュース取得・更新開始...")
        
        # staticディレクトリ作成
        os.makedirs('static', exist_ok=True)
        
        # フィード設定
        feeds = {
            'anime_game': {
                '4Gamer': 'https://www.4gamer.net/rss/news.xml',
                'GIGAZINE': 'https://gigazine.net/news/rss_2.0/',
                'Yahoo!エンタメ': 'https://news.yahoo.co.jp/rss/categories/entertainment.xml'
            },
            'tech': {
                'ITmedia': 'https://rss.itmedia.co.jp/rss/2.0/news_technology.xml',
                'PC Watch': 'https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf'
            },
            'weather': {
                'ウェザーニュース': 'https://weathernews.jp/s/topics/rss/rd.xml',
                'Yahoo!天気・災害': 'https://rss-weather.yahoo.co.jp/rss/earthquake.xml',
                'NHKニュース防災': 'https://www3.nhk.or.jp/rss/news/cat0.xml'
            }
        }
        
        # 結果格納
        result = {'collected_at': datetime.now().isoformat(), 'categories': {}}
        max_category = 5
        
        # 各カテゴリ処理
        for category, category_feeds in feeds.items():
            news_list = []
            
            for source, url in category_feeds.items():
                # RSS取得
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(url, headers=headers, timeout=10)
                    feed = feedparser.parse(response.content if response.status_code == 200 else url)
                    entries = feed.entries if feed.entries else []
                except:
                    entries = []
                
                # 記事処理
                for entry in entries[:10]:
                    # HTMLタグ除去
                    title = entry.get('title', '')
                    if title:
                        title = re.sub('<.*?>', '', title)
                        title = re.sub(r'\s+', ' ', title).strip()
                    
                    description = entry.get('description', '')
                    if description:
                        description = re.sub('<.*?>', '', description)
                        description = re.sub(r'\s+', ' ', description).strip()
                        description = description[:200] + "..." if len(description) > 200 else description
                    
                    news_list.append({
                        'title': title,
                        'description': description,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'source': source
                    })
            
            result['categories'][category] = news_list[:max_category]
        
        # JSONファイル保存
        with open('static/news.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ ニュース保存完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Flask API用のレスポンス
        return jsonify({'message': '取得完了', 'data': result})
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

# スタンドアロン実行用
if __name__ == "__main__":
    get_news()