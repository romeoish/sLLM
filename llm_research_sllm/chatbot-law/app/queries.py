import requests


def send_query_to_fastapi(query_text):
    response = requests.post(
        "http://localhost:8000/process_query/", json={"text": query_text}
    )
    return response.json() if response.status_code == 200 else "Error"
