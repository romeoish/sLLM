import asyncio

import renderer as r
import streamlit as st
import utils

st.set_page_config(page_title="법률이", page_icon=":books:")
utils.customise_design()

table_phrases = [
    "표",
    "엑셀",
    "테이블",
    "자세히",
    "짧게",
    "간략",
    "한문장",
    "두문장",
    "간결",
    "핵심",
    "요약",
    "결론",
    "중요한",
    "길게",
    "간단",
]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "안녕하세요! 법률이입니다. 궁금하신 것이 있으면 언제든 물어봐주세요!",
        }
    ]

chat_container = st.container()

for message in st.session_state.messages:
    r.render_previous_message(chat_container, message)

example_queries = [
    "임차인이 상속인 없이 사망한 경우 누가 임차인의 권리와 의무를 승계하나요?",
    "옥탑을 주거용으로 임차한 경우 주택임대차보호법이 적용되나요?",
    "전차인에게도 상가건물임대차보호법이 적용되나요?",
    "임차인이 법인인 경우 주택임대차 보호법 적용 범위는 어떻게돼?",
    # "임대차계약상의 임대인은 반드시 주택의 등기부상 소유자라야 하는지요?",
]

if len(st.session_state["messages"]) < 2:
    for example_query in example_queries:
        icon = "📋"
        if chat_container.button(
            f"{icon} {example_query}",
            key=example_query,
            help=example_query,
        ):
            st.session_state.messages.append({"role": "user", "content": example_query})
            st.rerun()

query = st.chat_input("질문을 입력해주세요.")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()


# if the last message was from the user, fetch and render the response
if st.session_state.messages[-1]["role"] == "user":
    asyncio.run(
        r.render_response_stream(
            st.session_state.messages[-1]["content"], chat_container, st.session_state
        )
    )
