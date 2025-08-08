from flask import Flask, jsonify
from flask_cors import CORS
from llm_chat import llm_chat_bp
from news import news_bp
from news_selector import news_selector_bp
from youtube import youtube_bp  

app = Flask(__name__)
CORS(app)

# Blueprintを登録
app.register_blueprint(llm_chat_bp)
app.register_blueprint(news_bp)
app.register_blueprint(news_selector_bp)  
app.register_blueprint(youtube_bp)  

if __name__ == '__main__':
    app.run(debug=True)