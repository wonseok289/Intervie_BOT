<면접 어시스턴트>
면접에 관련해 도움을 주기 위한 기능 탑재.
1. 모의면접
2. 면접 관련 팁
3. 면접 일정 예약
4. 면접 일정 확인
5. 나가기

main.py 실행 시, 면접 어시스턴트 gui창 등장.  그 내에서 다양한 기능 사용 가능.

주의:
In main.py, 

In this code:

class InterviewAssistant:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="<Enter your API key here>",
        )

Put your Openrouter api key in "api_key" variable.
