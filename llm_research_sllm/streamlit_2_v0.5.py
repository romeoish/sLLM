import streamlit as st
from streamlit_chat import message
import pandas as pd
from embedding_query import embedding_query
from answer_llm import answer_llm
from numpy import dot
from numpy.linalg import norm
from count_token import count_token

st.set_page_config(
page_title="농림봇",
page_icon=":books:")
provided_data = ""

st.title("농기평 x 솔리드이엔지 :red[LLM] :books:")
st.write("하이퍼클로바 기반 RAG기술을 적용한 전문LLM(v0.5)")
#st.write("국가연구개발혁신법 + 질의응답 데이터")

segments = pd.read_pickle("segment_qna_33726.pkl")
table_phrases = ['표','엑셀','테이블','자세히','짧게','간략','한문장','두문장','간결','핵심','요약','결론','중요한','길게','간단']
table_phrases2 = ['안녕','누구']

#if "conversation" not in st.session_state:
#    st.session_state.conversation = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant", 
                                        "content": "안녕하세요! 궁금하신 것이 있으면 언제든 물어봐주세요!"}]

for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

example_queries = [
    "총괄연구개발계획서에서 총괄주관연구개발기관과 총괄연구책임자란?",
    "공동연구개발기관에서 연구개발과제의 일부를 위탁하는 것이 가능한지?",
    "같은 연구개발기관이 하나의 연구개발과제에서 두 개 이상의 공동(위탁)연구개발기관으로 동시에 수행할 수 있는지?"
]

#if "button_clicked" not in st.session_state:
#    st.session_state.button_clicked = False

#show_example_queries = not st.session_state.button_clicked

# Display example queries as buttons
if "chat_history" in st.session_state and not st.session_state.chat_history:
    for example_query in example_queries:
        icon = "📋" 
        if st.button(f"{icon} {example_query}", key=example_query, help=example_query):
            st.session_state.messages.append({"role": "user", "content": example_query})
            with st.chat_message("user"):
                st.markdown(example_query)
            with st.chat_message("assistant"): 
                with st.spinner("답변을 생각중이에요..."):
                    preset_text = example_query
                    query_emb = embedding_query(preset_text)

                    top_2 = []
                    for i in range(len(segments)):
                        a = segments['vector'][i]
                        b = query_emb
                        cos_sim = dot(a, b)/(norm(a)*norm(b))
                        top_2.append(cos_sim)

                    if max(top_2) >= 0.975:
                        top_2 = sorted(range(len(top_2)), key=lambda i: top_2[i])[-2:]
                        provided_data = "[정보]: " + segments['origin'][top_2[1]] + segments['origin'][top_2[0]]
                    
                    if provided_data == "":
                        if any(phrase in query for phrase in table_phrases):
                            if 'chat_history' in st.session_state:
                                for interaction in st.session_state['chat_history']:
                                    provided_data = "[정보]: " + interaction['bot_answer']
                                    break

                    user_text = provided_data + "\n\n" + preset_text
                    answer = answer_llm(user_text)
                    token = count_token(preset_text)

                    current_interaction = {'user_input': example_query, 'bot_answer': answer}
                    st.session_state['chat_history'].insert(0,current_interaction)

                    st.markdown(answer)
                    if max(top_2) >= 0.975:
                        with st.expander("참고 문서 확인"):
                            st.markdown(f"참조한 정보: ①{segments['title'][top_2[1]]} {segments['page_num'][top_2[1]]}pg")
                            st.markdown(f"정보내용:①{segments['origin'][top_2[1]]}")
                            st.markdown(f"참조한 정보: ②{segments['title'][top_2[0]]} {segments['page_num'][top_2[0]]}pg")
                            st.markdown(f"정보내용:②{segments['origin'][top_2[0]]}")
                        
            st.session_state.messages.append({"role": "assistant", "content": answer})
    

####original query######
if query := st.chat_input("질문을 입력해주세요."):
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        #chain = st.session_state.conversation
            
        with st.spinner("답변을 생각중이에요..."):
            preset_text = query
            query_emb = embedding_query(preset_text)

            top_2 = []
            for i in range(len(segments)):
                a = segments['vector'][i]
                b = query_emb
                cos_sim = dot(a, b)/(norm(a)*norm(b))
                top_2.append(cos_sim)

            if max(top_2) >= 0.975:
                top_2 = sorted(range(len(top_2)), key=lambda i: top_2[i])[-2:]
                provided_data = "[정보]: " + segments['origin'][top_2[1]] + segments['origin'][top_2[0]]
                user_text = provided_data + "\n\n" + "[질문]: " +preset_text
                answer = answer_llm(user_text)
                
            if provided_data == "":
                if any(phrase in query for phrase in table_phrases):
                    if 'chat_history' in st.session_state:
                        for interaction in st.session_state['chat_history']:
                            provided_data = "[정보]: " + interaction['bot_answer']
                            break
                    user_text = provided_data + "\n\n" + "[질문]: " +preset_text
                    answer = answer_llm(user_text)
                elif any(phrase in query for phrase in ["안녕","이름","너","나"]):
                    answer = answer_llm(preset_text)
                else:
                    answer = "학습된 정보가 없습니다."

            
            #user_text = provided_data + "\n\n" + "[질문]: " +preset_text
            #answer = answer_llm(user_text)
            
            current_interaction = {'user_input': query, 'bot_answer': answer}
            st.session_state['chat_history'].insert(0,current_interaction)

            st.markdown(answer)
            if max(top_2) >= 0.975:
                with st.expander("참고 문서 확인"):
                    st.markdown(f"참조한 정보: ①{segments['title'][top_2[1]]} {segments['page_num'][top_2[1]]}pg")
                    st.markdown(f"정보내용:①{segments['origin'][top_2[1]]}")
                    st.markdown(f"참조한 정보: ②{segments['title'][top_2[0]]} {segments['page_num'][top_2[0]]}pg")
                    st.markdown(f"정보내용:②{segments['origin'][top_2[0]]}")
                 
    st.session_state.messages.append({"role": "assistant", "content": answer})


##v0.3: 안녕,등 general한 query에 대한 threshold 조정
##v0.4: reference 및 내용 반영, enter누를 시 prompt clear, 국가연구개발혁신법(33726호)