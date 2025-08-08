// server.js
const { TikTokLiveConnection, WebcastEvent } = require('tiktok-live-connector');

const connection = new TikTokLiveConnection('@aomiyayumena');

connection.on(WebcastEvent.CONNECT, (data) => {
    console.log('接続成功:', data.uniqueId);
});

connection.on(WebcastEvent.CHAT, (data) => {
    console.log(`${data.user.nickname}: ${data.comment}`);
});

connection.on(WebcastEvent.ERROR, (err) => {
    console.error('エラー:', err);
});

console.log('TikTok Live監視開始...');
connection.connect();