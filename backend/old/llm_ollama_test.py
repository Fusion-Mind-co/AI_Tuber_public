from ollama import chat , ChatResponse


# モデルを指定して実行
response: ChatResponse = chat(model='gemma3:4b', messages=[
  {
    'role': 'user',
    'content': 'こんにちは',
  },
])

print(response.message.content)