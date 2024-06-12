import json

import httpx
import queries as q
import streamlit as st
import CONSTANTS

QNA = CONSTANTS.QNA
DOCU = CONSTANTS.DOCU

def render_previous_message(chat_container, message):
    with chat_container.chat_message(message["role"]):
        st.markdown(message["content"])
        if "references" in message:
            col1, col2 = st.columns(2)
            references = message["references"]
            with col1:
                with st.expander("참조한 Q&A 정보"):
                    for i in range(len(references['meta'][QNA])):
                        st.markdown(f"({i+1}) {references['meta'][QNA][i]}")
                        st.markdown(f"{references['origin'][QNA][i]}")
            with col2:
                with st.expander("참조한 법령 정보"):
                    for i in range(len(references['meta'][DOCU])):
                        st.markdown(f"({i+1}) {references['meta'][DOCU][i]}")
                        st.markdown(f"{references['origin'][DOCU][i]}")

async def render_response_stream(query_text, chat_container, session_state):
    with chat_container.chat_message("assistant"):
        with st.empty():
            message = []
            references = {}
            print("Requesting response for query: ", query_text)
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    "http://localhost:8000/process_query/",
                    json={"text": query_text},
                ) as response:
                    current_mode = "id"
                    async for chunk in response.aiter_bytes():
                        line = chunk.decode("utf-8").strip()
                        if line.startswith("data:"):
                            data = line[len("data:") :].strip()
                            try:
                                data_json = json.loads(data)
                                if current_mode == "token":
                                    message.append(data_json["message"]["content"])
                                    st.markdown("".join(message))
                                elif current_mode == "json":
                                    references.update(data_json)
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}")
                        elif line.startswith("id:"):
                            current_mode = "id"
                        elif line.startswith("event:token"):
                            current_mode = "token"
                        elif line.startswith("event:result"):
                            current_mode = "result"
                        elif line.startswith("event:json"):
                            current_mode = "json"
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("참조한 Q&A 정보"):
                for i in range(len(references['meta'][QNA])):
                    st.markdown(f"({i+1}) {references['meta'][QNA][i]}")
                    st.markdown(f"{references['origin'][QNA][i]}")
        with col2:
            with st.expander("참조한 법령 정보"):
                for i in range(len(references['meta'][DOCU])):
                    st.markdown(f"({i+1}) {references['meta'][DOCU][i]}")
                    st.markdown(f"{references['origin'][DOCU][i]}")
    session_state["chat_history"].insert(0, {"user_input": query_text, "bot_answer": "".join(message)})
    session_state.messages.append({"role": "assistant", "content": "".join(message), "references": references})


def render_response(query_text, chat_container, session_state):
    with chat_container.chat_message("assistant"):
        with st.spinner("답변을 생각중이에요..."):
            response = q.send_query_to_fastapi(query_text)
            if response == "Error":
                with st.chat_message("assistant"):
                    st.markdown("에러가 발생했습니다. 다시 시도해주세요.")
                return
            response, origin, meta, cos_sim = (
                response.get("response"),
                response.get("origin"),
                response.get("meta"),
                response.get("cos_sim"),
            )

            keysQna = []
            valuesQna = []

            for key, value in origin[QNA].items():
                keysQna.append(key)
                valuesQna.append(value)

            keysMetaQna = []
            valuesMetaQna = []

            for key, value in meta[QNA].items():
                keysMetaQna.append(key)
                valuesMetaQna.append(value)

            keysDocu = []
            valuesDocu = []

            for key, value in origin[DOCU].items():
                keysDocu.append(key)
                valuesDocu.append(value)

            keysMetaDocu = []
            valuesMetaDocu = []

            for key, value in meta[DOCU].items():
                keysMetaDocu.append(key)
                valuesMetaDocu.append(value)

            current_interaction = {"user_input": query_text, "bot_answer": response}
            session_state["chat_history"].insert(0, current_interaction)
            st.markdown(response)
            if cos_sim[QNA] >= 0.970 and cos_sim[DOCU] >= 0.970:
                with st.expander("참조한 Q&A 정보"):
                    st.markdown(f"① {valuesMetaQna[0]}")
                    st.markdown(f"{valuesQna[0]}")
                    # st.markdown(f"② {valuesMetaQna[1]}")
                    # st.markdown(f"{valuesQna[1]}")
                with st.expander("참조한 법령 정보"):
                    st.markdown(f"① {valuesMetaDocu[0]}")
                    st.markdown(f"{valuesDocu[0]}")
                    # st.markdown(f"② {valuesMetaDocu[1]}")
                    # st.markdown(f"{valuesDocu[1]}")
    session_state.messages.append({"role": "assistant", "content": response})
