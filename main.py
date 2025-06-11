from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<Enter your API key here>",
)

messages = [{
    'role': 'system',
    'content': 'Recommend one dinner dish that can be made with the ingredients provided by the user, and explain the recipe.'
}]


while True:
    msg = input('user prompt: ')

    if msg.strip().lower() == 'q':
        break

    messages.append({
        'role': 'user',
        'content': msg
    })

    completion = client.chat.completions.create(
        model="qwen/qwen3-14b:free",
        messages=messages
    )
    messages.append(completion.choices[0].message)
    print(completion.choices[0].message.content)

print()