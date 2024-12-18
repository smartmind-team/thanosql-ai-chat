import requests

# HOST = "http://211.218.150.152:8826"
HOST = "http://localhost:8826"
PATH = "/chat"


def test_chat():
    test_msg = "Hello, world!"
    data = {
        "messages": [
            {
                "id": "17344943590151734494364791",
                "createdAt": "2024-12-18T03:59:24.791Z",
                "role": "user",
                "content": test_msg,
            }
        ],
        "prompt_tables": [],
        "session_id": "1734494359015",
    }

    # stream=True로 설정하여 스트리밍 응답 받기
    with requests.post(f"{HOST}{PATH}", json=data, stream=True) as response:
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
        else:
            print(f"Response: {response.status_code}")
            answer = ""
            # 스트림으로 들어오는 데이터를 처리
            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode("utf-8")
                    answer += decoded_chunk

        print(f"Answer: {answer}")

if __name__ == "__main__":
    test_chat()
