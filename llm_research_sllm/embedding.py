import base64
import json
import http.client

class CompletionExecutor_Emb:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/testapp/v1/api-tools/embedding/clir-emb-dolphin/99d80c7306c343a2b8abf87d6d06f95a', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['embedding']
        else:
            return 'Error'


def embedding_text(response_text):
    completion_executor = CompletionExecutor_Emb(
        host='clovastudio.apigw.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY1aM5JpMNr1vYMQHOi/ifhUlI8DadYG/B7WrQXcfae6ENwjhBlll1AfPSjNxQOF/HhEZpbXGKTf1Y1EX7/36ZJ6fmTWKTIE6imyNWI4tsF/du7EUTA6y99vfE2aK6kDca/EYCCa5wKQkPf21VDUi0X5wPDIJyIVVT8eTausRz5/f',
        api_key_primary_val = 'UBwKtmApo6wH5wCrtUtp7AqxpnkNC9aLSWvxFNSE',
        request_id='ee153eb8080d4c9cb7758508c1424210'
    )
    vectors = []
    i = 1
    for segmentation in response_text:
        print(i)
        print(segmentation)
        segmentation_str = ""
        for line in segmentation:
            segmentation_str += line +' '
        request_data = json.loads(f"""{{"text":"{segmentation_str[:450]}"}}""",strict=False)
        response_text_emb = completion_executor.execute(request_data)
        print(response_text_emb)
        vectors.append(response_text_emb)
        i = i+1
    return vectors