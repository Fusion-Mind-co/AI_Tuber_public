import { useState } from "react";
import axios from "axios";

function App() {
  // AI設定
  const [aiName, setAiName] = useState("あみたろう");
  const [aiPersonality, setAiPersonality] =
    useState("明るくて元気で親しみやすい女の子。");

  // メッセージ
  const [inputMessage, setInputMessage] = useState("");
  const [userMessage, setUserMessage] = useState("");
  const [responseData, setResponseData] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // LLM設定
  const [provider, setProvider] = useState("gemini");
  const [llmModel, setLlmModel] = useState("gemini-2.0-flash-exp");

  // ============================ニュース===============================

  // 取得する最大ニュース数(カテゴリ別)
  const [maxNews, setMaxNews] = useState(5);
  // 取得したニュースデータ
  const [newsData, setNewsData] = useState(null);
  // ローディング
  const [isNewsLoading, setIsNewsLoading] = useState(false);
  const [showNews, setShowNews] = useState(false);

  // ============================YouTubeコメント================================

  // 配信ID
  const [videoId, setVideoId] = useState("");

  // ======================表示/非表示の状態管理 =============================
  // AI設定
  const [showLLMSettings, setShowLLMSettings] = useState(false);
  // YouTube
  const [showYouTubeComment, setShowYouTubeComment] = useState(false);
  // ニュース
  const [showNewsSection, setShowNewsSection] = useState(false);

  const providers = ["gemini", "ollama"];
  const modelsByProvider = {
    gemini: ["gemini-2.0-flash-exp", "gemini-2.5-flash-lite"],
    ollama: ["gemma3:4b", "gemma3:12b"],
  };

  // プロバイダー変更時にモデルを自動切り替え 🆕
  const handleProviderChange = (newProvider) => {
    setProvider(newProvider);

    // デフォルトモデルに自動切り替え
    const defaultModels = {
      gemini: "gemini-2.0-flash-exp",
      ollama: "gemma3:4b",
    };

    const defaultModel = defaultModels[newProvider];
    if (defaultModel) {
      setLlmModel(defaultModel);
    }
  };

  // ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

  // YouTubeコメント関連の状態追加
  const [commentStatus, setCommentStatus] = useState({
    isCollecting: false,
    commentCount: 0,
    lastUpdated: null,
  });

  // コメント収集開始
  const fetchYouTubeComment = async () => {
    if (!videoId.trim()) {
      alert("配信IDを入力してください");
      return;
    }

    if (videoId.length !== 11) {
      alert("配信IDは11文字である必要があります");
      return;
    }

    try {
      const response = await axios.post("/api/youtube", {
        video_id: videoId,
      });

      if (response.data.status === "started") {
        alert("コメント収集を開始しました");
        setCommentStatus((prev) => ({ ...prev, isCollecting: true }));
        // 定期的に状態をチェック
        checkCommentStatus();
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || "YouTubeコメント取得失敗";
      alert(`エラー: ${errorMessage}`);
      console.error("YouTube comment fetch error:", error);
    }
  };

  // 状態チェック関数（改善版）
  const checkCommentStatus = async () => {
    if (!videoId) return;

    try {
      const response = await axios.get(`/api/youtube/status/${videoId}`);
      const statusData = response.data;

      setCommentStatus({
        isCollecting: statusData.is_collecting,
        commentCount: statusData.comment_count,
        lastUpdated: new Date().toLocaleTimeString("ja-JP"),
      });

      console.log("収集状況:", statusData);

      // まだ収集中の場合、5秒後に再チェック
      if (statusData.is_collecting) {
        setTimeout(checkCommentStatus, 5000);
      }
    } catch (error) {
      console.error("状態チェックエラー:", error);
      // エラーが発生した場合は収集停止とみなす
      setCommentStatus((prev) => ({ ...prev, isCollecting: false }));
    }
  };

  // コメント収集停止
  const stopYouTubeComment = async () => {
    if (!videoId) {
      alert("配信IDが設定されていません");
      return;
    }

    try {
      const response = await axios.post(`/api/youtube/stop/${videoId}`);
      alert(response.data.message);
      setCommentStatus({
        isCollecting: false,
        commentCount: 0,
        lastUpdated: null,
      });
    } catch (error) {
      console.error("停止エラー:", error);
      alert("停止に失敗しました");
    }
  };

  // ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

  // ニュース取得（更新も含む）
  const fetchNews = async () => {
    setIsNewsLoading(true);
    try {
      const response = await axios.post("/api/news/refresh");
      setNewsData(response.data.data);
      // 取得完了後は概要のみ表示（モーダルは開かない）
    } catch (error) {
      alert("ニュース取得失敗");
    } finally {
      setIsNewsLoading(false);
    }
  };

  // ニュース厳選機能 🆕
  const selectBestNews = async () => {
    if (!newsData) {
      alert("先にニュースを取得してください");
      return;
    }

    setIsNewsLoading(true);
    try {
      // 1. LLMでニュース厳選
      const selectResponse = await axios.post("/api/news/select", {
        ai_personality: aiPersonality,
        provider: provider,
        llm_model: llmModel,
      });

      const selectedNews = selectResponse.data.selected_news;
      console.log("🎯 厳選されたニュース:", selectedNews);

      // 2. 厳選されたニュースを自動で話題化
      const topicMessage = `「そういえば」や「ところで」のような接続詞から会話を始め、このニュースを軽く紹介しつつ、コメントをしてください。そして会話が続くようにリスナーに話題を投げかけてください：\n\nタイトル: ${selectedNews.title}\n概要: ${selectedNews.description}\nソース: ${selectedNews.source}`;

      setIsLoading(true);
      const chatResponse = await axios.post("/api/llmchat", {
        message: topicMessage,
        aiName,
        aiPersonality,
        provider,
        llm_model: llmModel,
      });

      setResponseData(chatResponse.data.message);
      setUserMessage(`🎯 厳選ニュース: ${selectedNews.title}`);
      setInputMessage("");
    } catch (error) {
      console.error("厳選エラー:", error);
      alert("ニュース厳選に失敗しました");
    } finally {
      setIsNewsLoading(false);
      setIsLoading(false);
    }
  };

  // ニュースを話題にする
  const sendNewsAsTopic = async (newsItem) => {
    const topicMessage = `「そういえば」や「ところで」のような接続詞から会話を始め、このニュースを軽く紹介しつつ、コメントをしてください。そして会話が続くようにリスナーに話題を投げかけてください：\n\nタイトル: ${newsItem.title}\n概要: ${newsItem.description}\nソース: ${newsItem.source}`;

    setIsLoading(true);
    try {
      const response = await axios.post("/api/llmchat", {
        // 直接Flaskサーバーに
        message: topicMessage,
        aiName,
        aiPersonality,
        provider,
        llm_model: llmModel,
      });
      setResponseData(response.data.message);
      setUserMessage(`📰 ${newsItem.title}`);
      setInputMessage("");
    } catch (error) {
      setResponseData("エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  // メッセージ送信
  const sendMessage = async () => {
    if (!inputMessage.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post("/api/llmchat", {
        // 直接Flaskサーバーに
        message: inputMessage,
        aiName,
        aiPersonality,
        provider,
        llm_model: llmModel,
      });
      setResponseData(response.data.message);
      setUserMessage(inputMessage);
      setInputMessage("");
    } catch (error) {
      setResponseData("エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  const categoryNames = {
    anime_game: "🎮 アニメ・ゲーム",
    tech: "📱 テック",
    weather: "🌤️ 天気・災害",
  };

  // =======================================================================================
  // =======================================JSX=============================================
  // =======================================================================================

  return (
    <div className="max-w-4xl mx-auto p-4">
      {/* LLM設定 */}
      <div className="border-2 border-gray-300 rounded-lg p-4 bg-white shadow-md mb-4">
        <h2
          className="text-xl font-bold mb-4 cursor-pointer flex justify-between items-center hover:text-blue-600"
          onClick={() => setShowLLMSettings(!showLLMSettings)}
        >
          <span>⚙️ AI設定</span>
          <span className="text-lg">{showLLMSettings ? "▼" : "▶"}</span>
        </h2>

        {showLLMSettings && (
          <>
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  プロバイダー
                </label>
                <select
                  value={provider}
                  onChange={(e) => handleProviderChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                >
                  {providers.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  モデル
                </label>
                <select
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                >
                  {modelsByProvider[provider]?.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  AIの名前
                </label>
                <input
                  type="text"
                  placeholder="AIの名前を入力"
                  value={aiName}
                  onChange={(e) => setAiName(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  AIの性格・口調
                </label>
                <textarea
                  type="text"
                  placeholder="AIの性格を入力"
                  value={aiPersonality}
                  onChange={(e) => setAiPersonality(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
            </div>
          </>
        )}
      </div>

      {/* YouTubeコメント */}
      <div className="border-2 border-gray-300 rounded-lg p-4 bg-white shadow-md mb-4">
        <h2
          className="text-xl font-bold mb-4 cursor-pointer flex justify-between items-center hover:text-blue-600"
          onClick={() => setShowYouTubeComment(!showYouTubeComment)}
        >
          <span>▶ YouTubeコメント</span>
          <span className="text-lg">{showYouTubeComment ? "▼" : "▶"}</span>
        </h2>

        {showYouTubeComment && (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                配信ID(11ケタ)
              </label>
              <input
                type="text"
                placeholder="配信ID(11ケタ)を入力"
                value={videoId}
                onChange={(e) => setVideoId(e.target.value)}
                className="w-full px-3 py-2 border rounded"
                maxLength={11}
              />
            </div>

            {/* ステータス表示 */}
            {commentStatus.isCollecting && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-green-700 font-semibold">
                      🔴 収集中...
                    </span>
                    <div className="text-sm text-green-600">
                      コメント数: {commentStatus.commentCount}件
                      {commentStatus.lastUpdated && (
                        <span className="ml-2">
                          最終更新: {commentStatus.lastUpdated}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={stopYouTubeComment}
                    className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm font-semibold"
                  >
                    ⏹ 停止
                  </button>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={fetchYouTubeComment}
                disabled={commentStatus.isCollecting || !videoId.trim()}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded font-semibold disabled:opacity-50"
              >
                {commentStatus.isCollecting
                  ? "📡 収集中..."
                  : "▶ コメント取得開始"}
              </button>

              {videoId && (
                <button
                  onClick={checkCommentStatus}
                  disabled={commentStatus.isCollecting}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded font-semibold disabled:opacity-50"
                >
                  🔄 状態確認
                </button>
              )}
            </div>
          </>
        )}
      </div>

      {/* ニュース */}
      <div className="border-2 border-blue-300 rounded-lg p-4 bg-blue-50 shadow-md mb-4">
        <h2
          className="text-xl font-bold mb-4 cursor-pointer flex justify-between items-center hover:text-blue-600"
          onClick={() => setShowNewsSection(!showNewsSection)}
        >
          <span>📰 ニュース</span>
          <span className="text-lg">{showNewsSection ? "▼" : "▶"}</span>
        </h2>

        {showNewsSection && (
          <>
            <div className="flex gap-3 mb-4">
              <button
                onClick={fetchNews}
                disabled={isNewsLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold disabled:opacity-50"
              >
                {isNewsLoading ? "📡 取得中..." : "🔄 ニュース取得"}
              </button>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                カテゴリ別最大取得ニュース数
              </label>
              <input
                type="number"
                value={maxNews}
                onChange={(e) => setMaxNews(e.target.value)}
              />

              {newsData && (
                <button
                  onClick={selectBestNews}
                  disabled={isNewsLoading || isLoading}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-semibold disabled:opacity-50"
                >
                  {isNewsLoading || isLoading
                    ? "🤖 厳選中..."
                    : "🎯 おすすめニュース"}
                </button>
              )}
            </div>

            {/* ニュース概要表示 */}
            {newsData && (
              <div className="p-3 bg-white border rounded-lg">
                <p className="text-sm mb-2">
                  📅 取得:{" "}
                  {new Date(newsData.collected_at).toLocaleString("ja-JP")}
                </p>
                <div className="flex gap-4 text-sm">
                  {Object.entries(newsData.categories).map(
                    ([category, items]) => (
                      <span
                        key={category}
                        className="bg-gray-100 px-2 py-1 rounded"
                      >
                        {categoryNames[category]} ({items.length}件)
                      </span>
                    )
                  )}
                </div>
                <button
                  onClick={() => setShowNews(true)}
                  className="mt-3 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded font-semibold"
                >
                  📰 ニュース一覧を開く
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* ニュースモーダル */}
      {showNews && newsData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            {/* モーダルヘッダー */}
            <div className="flex justify-between items-center p-4 border-b">
              <h2 className="text-xl font-bold">📰 ニュース一覧</h2>
              <button
                onClick={() => setShowNews(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            {/* モーダルコンテンツ */}
            <div className="flex-1 overflow-y-auto p-4">
              <p className="text-sm mb-4 text-gray-600">
                📅 取得:{" "}
                {new Date(newsData.collected_at).toLocaleString("ja-JP")}
              </p>

              {Object.entries(newsData.categories).map(([category, items]) => (
                <div key={category} className="mb-6">
                  <h3 className="text-lg font-bold mb-3 border-b pb-2">
                    {categoryNames[category] || category} ({items.length}件)
                  </h3>
                  <div className="space-y-3">
                    {items.map((item, index) => (
                      <div
                        key={index}
                        className="bg-gray-50 border rounded-lg p-3"
                      >
                        <div className="flex justify-between gap-3">
                          <div className="flex-1">
                            <h4 className="font-semibold mb-1">{item.title}</h4>
                            {item.description && (
                              <p className="text-sm text-gray-600 mb-2">
                                {item.description}
                              </p>
                            )}
                            <div className="text-xs text-gray-500">
                              📺 {item.source} | 📅 {item.published}
                            </div>
                          </div>
                          <div className="flex flex-col gap-2">
                            <button
                              onClick={() => {
                                sendNewsAsTopic(item);
                                setShowNews(false); // モーダル閉じる
                              }}
                              disabled={isLoading}
                              className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded text-xs font-semibold disabled:opacity-50"
                            >
                              💬 話題化
                            </button>
                            {item.link && (
                              <a
                                href={item.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-xs font-semibold text-center"
                              >
                                🔗 記事
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* モーダルフッター */}
            <div className="border-t p-4">
              <button
                onClick={() => setShowNews(false)}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded font-semibold"
              >
                閉じる
              </button>
            </div>
          </div>
        </div>
      )}

      {/* メッセージ */}
      <div className="border-2 border-gray-300 rounded-lg p-4 bg-white shadow-md">
        <h2 className="text-xl font-bold mb-4">💬 チャット</h2>

        <div className="mb-4 p-3 bg-blue-50 border rounded">
          <p className="text-sm">
            <strong>AI:</strong> {aiName} | <strong>性格:</strong>{" "}
            {aiPersonality}
          </p>
        </div>
        {/* デバッグ用ボタン */}
        <button
          onClick={() => setInputMessage("こんにちは")}
          className="border-2 border-gray-300 hover:bg-gray-100  rounded-lg p-1 bg-white shadow-md"
        >
          こんにちは
        </button>
        <button
          onClick={() => setInputMessage("おつかれー")}
          className="border-2 border-gray-300 hover:bg-gray-100  rounded-lg p-1 bg-white shadow-md"
        >
          おつかれー
        </button>
        {/* ーーーーーーーーー */}
        <div className="flex gap-3 mb-4">
          <textarea
            type="text"
            placeholder="メッセージを入力"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && !isLoading && sendMessage()}
            disabled={isLoading}
            className="flex-1 px-4 py-2 border rounded focus:border-blue-500 disabled:bg-gray-100"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded font-semibold disabled:opacity-50"
          >
            {isLoading ? "送信中..." : "送信"}
          </button>
        </div>

        {responseData && (
          <div className="p-4 bg-gray-50 border rounded">
            <h3 className="font-semibold mb-2">ユーザー:</h3>
            <p className="mb-4 whitespace-pre-wrap">{userMessage}</p>
            <h3 className="font-semibold mb-2">{aiName}:</h3>
            <p className="whitespace-pre-wrap">{responseData}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
