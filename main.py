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

print('저는 면접 어시스턴트입니다. 무슨 유형의 면접을 생각중이신가요? ')

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
        ask = input("""
                    시작하시겠습니까? 다음 번호 중 하나를 선택하세요.
                    1. 모의면접
                    2. 면접 관련 팁
                    3. 면접 일정 예약
                    4. 면접 일정 확인
                    5. 나가기
                    """)

        if ask.strip().lower() == '1':
            messages.append({
                'role': 'user',
                'content': 'Give me one interview question.'
            })

            completion = client.chat.completions.create(
                model="qwen/qwen3-14b:free",
                messages=messages
            )
            messages.append(completion.choices[0].message)
            print('Q.', completion.choices[0].message.content)

            answer = input('A. ')

            if answer.strip().lower() == 'q':
                break

            messages.append({
                'role': 'user',
                'content': answer
            })

            completion = client.chat.completions.create(
                model="qwen/qwen3-14b:free",
                messages=messages
            )
            messages.append(completion.choices[0].message)
            print(completion.choices[0].message.content)
        elif ask.strip().lower() == '2':
            #TODO (이 블럭에서 코드 짜주세요., pass 지우셔도 됨.)
            pass
        elif ask.strip().lower() == '3':
            #TODO
            pass
        elif ask.strip().lower() == '4':
            #TODO
            pass
        elif ask.strip().lower() == '5':
            print('Thank you for your time. Goodbye.')
            break
        else:
            continue

        


