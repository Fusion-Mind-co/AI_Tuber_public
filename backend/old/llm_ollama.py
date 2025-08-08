from ollama import chat , ChatResponse


# モデルを指定して実行
response: ChatResponse = chat(model='gemma3:4b', messages=[
  {
    'role': 'system',
    'content': 'あなたの名前は「さくら」です。親しみやすく、丁寧で優しい性格のAIアシスタントとして振る舞ってください。'
  },
  {
    'role': 'user',
    'content': 'こんにちは'
  },
])

print(response.message.content)