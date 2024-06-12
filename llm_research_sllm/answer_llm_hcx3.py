import requests
import json


class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            #'Accept': 'text/event-stream'
        }
        result_lines = []
        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    #print(line.decode("utf-8"))
                    result_lines.append(line.decode("utf-8"))
        result_json = json.loads(''.join(result_lines))
        return result_json

def answer_llm(user_text):
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY2W+zUGmm5SHgsDJBy5F7SFNuVY1tJcJTyhUXLrTnekZA/u1pZ4oBJHvLUdIsvlF7IuPFlGGtnb832hcmD+YIJbrR9NUMFBsJ5TMyrl94jBAQ2amx/sFbZWnHAsqeuxxWMkUq0qXdhIUJ/VMhvlGCacQtF6NOAIpnGFb+7MURctOL5RYpMpwUwrB2LEgz8CMbWMKLGxpeliSD1a7IYTafiU=',
        api_key_primary_val='UBwKtmApo6wH5wCrtUtp7AqxpnkNC9aLSWvxFNSE',
        request_id='2a83d1218c534c27a648616e64ed9abb'
    )

    preset_text = [{"role":"system","content": "\n".join([
            "-너의 이름은 연구특구봇이야.",
            "-너는 연구특구 규정 전문 챗봇이야.",
            "-주어진 [정보]만 활용해서 대답해.",
            "-사례 또는 예시와 함께 대답해.",
            # "-[정보]가 없으면 정보가 없습니다라고 대답해줘.",
            "-주어진 [정보]들을 읽고 [질문]에 답변을 작성해줘.",
            "-주어진 [정보]에서만 답변을 만들어줘.",
            "-[질문]과 [정보]가 관련이 없더라도 [정보]의 내용을 설명해줘.",
            #"-[질문]에 대해서만 답변해.",
            # "-[질문]에서 인사나 안부를 물으면 같이 인사나 안부로 대답해줘.",
            #"-[질문]에 해당되는 정보가 없으면 질문에 해당되는 정보가 없다고 대답해줘.",
            # "-[정보]의 모든 내용을 설명과 함께 대답해줘"
        ])},{"role":"user","content":user_text}]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 1500,
        'temperature': 0.5,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': True
    }

    response_text = completion_executor.execute(request_data)
    return response_text['result']['message']['content']