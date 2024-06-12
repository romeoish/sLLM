from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from embedding_query import embedding_query
from answer_llm_hcx3 import answer_llm
import faiss
from numpy import dot
from numpy.linalg import norm
from sllm import infer
#from langchain.retrievers import BM25Retriever, EnsembleRetriever

app = FastAPI()  # FastAPI 인스턴스를 생성
segmentsQna = pd.read_pickle("research_100p_3.pkl")

vectorsQna = np.array(segmentsQna["vector2"].tolist()).astype(
    "float32"
)  # 벡터를 numpy 배열로 변환하고 float32 형식으로 변환
dimensionQna = vectorsQna.shape[1]  # 벡터 차원 계산

indexQna = faiss.IndexFlatL2(dimensionQna)  # Using L2 distance for similarity
indexQna.add(vectorsQna)


class Query(BaseModel):
    text: str  # Pydantic 모델을 사용하여 쿼리의 구조 정의


# cosine similarity 계산
# def get_top_segments(query_emb, segments, top_n=2):
#    cos_sims = [np.dot(query_emb, seg_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(seg_emb)) for seg_emb in segments['vector']]
#    top_indices = np.argsort(cos_sims)[-top_n:]
#    return " ".join(segments['Contents'][idx] for idx in top_indices)


instruction = """
    -너의 이름은 연구특구봇이야.,
    -너는 연구특구 규정 전문 챗봇이야.,
    -주어진 [정보]만 활용해서 대답해.,
    -주어진 [정보]들을 읽고 [질문]에 답변을 작성해줘.",
    -주어진 [정보]에서만 답변을 만들어줘.,
    -[질문]과 [정보]가 관련이 없더라도 [정보]의 내용을 설명해줘.,
"""


@app.post("/process_query/")
async def process_query(query: Query):
    try:
        query_emb = np.array(embedding_query(query.text)).astype(
            "float32"
        )  # 쿼리 임배딩 및 numpy 배열로 변환
        top_n = 1
        distancesQna, indicesQna = indexQna.search(
            query_emb.reshape(1, -1), top_n
        )  # Faiss유사한 벡터 찾기

        firstSegmentQna = segmentsQna["vector"][indicesQna[0][0]]
        cosSimQna = dot(query_emb, firstSegmentQna) / (
            norm(query_emb) * norm(firstSegmentQna)
        )  # 수동으로 cosine 구하기
        print("qna cosine similarity: " + str(cosSimQna))


        #if cosSimQna >= 0.970:
            # Retrieve results
        top_segments = (
            "[정보]: "
            + " ".join(segmentsQna["chunk"][idx] for idx in indicesQna[0])
        )
        user_text = top_segments + "\n\n" + query.text
        #response = answer_llm(user_text)
        response = infer(instruction=instruction, input_text=user_text)
        print(user_text)
        print(response)
        return {
            "response": response,
            "origin": [
                segmentsQna["chunk"][indicesQna[0]],
            ],
            "meta": [
                segmentsQna["Meta"][indicesQna[0]],
            ],
            "cos_sim": [cosSimQna],
            }
        # else:
        #     print("unrelated")
        #     user_text = "정보가 없습니다." + "\n\n" + query.text
        #     response = answer_llm(user_text)
        #     print(response)
        #     return {
        #         "response": response,
        #         "origin": [
        #             segmentsQna["chunk"][indicesQna[0]],
        #         ],
        #         "meta": [
        #             segmentsQna["Meta"][indicesQna[0]],
        #         ],
        #         "cos_sim": [cosSimQna],
        #     }
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))
