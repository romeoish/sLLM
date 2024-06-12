import requests
import streamlit as st
from streamlit.components.v1 import html
import base64

st.set_page_config(page_title="연구특구봇", page_icon=":books:")

# Define the full-width image URL
# Define the relative path to the image in the static folder

header_image_path = "static/header.png"
header_image_data = base64.b64encode(open(header_image_path, "rb").read()).decode()

bg_image_path = "static/bg.png"
bg_image_data = base64.b64encode(open(bg_image_path, "rb").read()).decode()

st.markdown(
    f"""
        <style>
        .element-container:has(iframe[height="0"]) {{
            display: none;
        }}

        /* Reduce padding-top */
        [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] {{
            padding-top: 1rem;
        }}

        /* Remove the gap between all elements */
        [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] > [data-testid="stVerticalBlockBorderWrapper"] > .st-emotion-cache-1wmy9hl.e1f1d6gn1 > [data-testid="stVerticalBlock"] {{
            gap: 0rem;
        }}

        /* Add gap after elements explicitly. If you want to have a gap between elements, copy the line here and change the selector at the end. */
        [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] > [data-testid="stVerticalBlockBorderWrapper"] > .st-emotion-cache-1wmy9hl.e1f1d6gn1 > [data-testid="stVerticalBlock"] >.stChatMessage,
        [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] > [data-testid="stVerticalBlockBorderWrapper"] > .st-emotion-cache-1wmy9hl.e1f1d6gn1 > [data-testid="stVerticalBlock"] > .stButton  {{
            margin-bottom: 1rem;
        }}
        </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
        .full-width-header {{
            position: relative;
            z-index: 9999999999;
            background-color: #eadce1;
            width: 100vw;
            height: 300px;  /* Adjust the height as needed */
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;  /* Set the text color to contrast with the image */
            font-size: 24px;  /* Set the font size as needed */
            overflow: hidden;  /* Hide the scrollbars */
        }}
        .full-width-header img {{
            width: auto;
            min-height: 100%;
            height: 100%;
            object-fit: contain;
        }}
        iframe {{
            height: 0rem;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    .reportview-container {
        background-color: transparent;
    }
    .sidebar .sidebar-content {
        background-color: transparent;
    }
    .stChatFloatingInputContainer {
        background-color: transparent;
    }
    .stApp{
        background-color: transparent;
    }
    .st-emotion-cache-j5kadu{
        width: 100vw;
        left: 0;
        display: flex;
        justify-content: center;
        background-color: rgba(232, 232, 227, 0.5);
        border-top: 1px solid rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);  /* Add the frosted glass effect */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

html(
    f"""
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        const customHeader = window.parent.document.querySelector('.full-width-header');

        if (customHeader) {{
            return;
        }}
        const stApp = window.parent.document.querySelector('[data-testid="stApp"]');
        const stAppViewContainer = window.parent.document.querySelector(
            '[data-testid="stAppViewContainer"]'
        );
        const stHeader = window.parent.document.querySelector(
            '[data-testid="stHeader"]'
        );

        // set position relative to app and app view container
        stApp.style.position = 'relative';
        stAppViewContainer.style.position = 'relative';

        // add an element as the first child of stAppViewContainer
        const newElement = document.createElement('div');
        newElement.className = 'full-width-header';

        // add an image as the first child of newElement
        const img = document.createElement('img');
        img.src = 'data:image/png;base64,{header_image_data}';
        img.alt = 'Header Image';
        newElement.appendChild(img);

        stHeader.insertAdjacentElement('afterend', newElement);
    }});
</script>
    """,
    height=0,
)

page_bg_img = f"""
<style>
body {{
    background-image: url(data:image/png;base64,{bg_image_data});
    background-size: cover;
    background-attachment: fixed;
    width: 100vw;
    height: 100vh;
    overflow-x: hidden;
    overflow-y: scroll;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

QNA = 0
DOCU = 1

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
        {"role": "assistant", "content": "안녕하세요! 저는 솔리드이엔지에서 만든 연구특구봇이에요. 궁금하신 것이 있으면 언제든 물어보세요!"}
    ]

chat_container = st.container()


def send_query_to_fastapi(query_text):
    response = requests.post(
        "http://localhost:8000/process_query/", json={"text": query_text}
    )
    return response.json() if response.status_code == 200 else "Error"


def render_response(query_text):
    with chat_container.chat_message("assistant"):
        with st.spinner("답변을 생각중이에요..."):
            response = send_query_to_fastapi(query_text)
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

            current_interaction = {"user_input": query_text, "bot_answer": response}
            st.session_state["chat_history"].insert(0, current_interaction)
            st.markdown(response)
            if cos_sim[QNA] >= 0.970:
                with st.expander("참조한 Q&A 정보"):
                    st.markdown(f"① {valuesMetaQna[0]}")
                    st.markdown(f"{valuesQna[0]}")
                    # st.markdown(f"② {valuesMetaQna[1]}")
                    # st.markdown(f"{valuesQna[1]}")

    st.session_state.messages.append({"role": "assistant", "content": response})


for message in st.session_state.messages:
    with chat_container.chat_message(message["role"]):
        st.markdown(message["content"])

example_queries = [
    "진흥재단이 세입세출결산보고서에 첨부하여 제출해야 하는 서류는 무엇인가요?",
    "배우자 사망시 휴가는 몇일이야?",
    "육아휴직은 어떻게 쓸 수 있어?",
    "이사장이 이사회에 보고해야 하는 사항들은 무엇인가요?",
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

if query := st.chat_input("질문을 입력해주세요."):
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()


# if the last message was from the user, fetch and render the response
if st.session_state.messages[-1]["role"] == "user":
    render_response(st.session_state.messages[-1]["content"])

    