from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

messages = [{
    'role': 'system',
    'content': 'You are a helpful interview assistant. \
                If you are given type of interview(ex: soccer club, AI graduate school), \
                you say "OK, I\'m ready." and you are ready to start the interview about given type.(Don\'t reply except "OK, I\'m ready.") \
                And then whenever I ask you a question, you will ask the one interview question. \
                If I reply to your question, you will evaluate my answer(점수: 1점 ~ 5점) and give me the feedback. \
                If I say "I want to quit", you will say "Thank you for your time. Goodbye." and end the interview. \
                And you must reply in Korean. \
                '
}]

print('I\'m interview assistant. What type of interview do you want? ')

msg = input(': ')

if msg.strip().lower() == 'q':
    print()
else:
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


    while True:
        ask = input('Want question? ')

        if ask.strip().lower() == 'y':
            pass
        elif ask.strip().lower() == 'q':
            break
        else:
            continue

        


