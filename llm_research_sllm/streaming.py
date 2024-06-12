import requests


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
            'Accept': 'text/event-stream'
        }

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    print(line.decode("utf-8"))


if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY6oIreh62el/WjGuU82pvCu1zm0rESGXsU9qcnwAND4+5Dl9609ESGb6yM4VcCE/S9GnPXb+PzgvDytCAjhJ89VaobjaHgvNOqCw2whTDh3quU2orvkjTMZiRIsX+kIYBa+O4Tshd+3FhCIACgTpYmIcyRxF2UJ5QcQWJbHMX2vLYMISM5wzbxi/Pw7VG+rDAPpiOHvyQI6o+fZIckOgGKY=',
        api_key_primary_val='UBwKtmApo6wH5wCrtUtp7AqxpnkNC9aLSWvxFNSE',
        request_id='9cfcbd28ebe940b4a313ae816d1b0e34'
    )

    preset_text = [{"role":"system","content":""},{"role":"user","content":"너의 이름은 뭐야?"}]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.5,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }

    print(preset_text)
    completion_executor.execute(request_data)