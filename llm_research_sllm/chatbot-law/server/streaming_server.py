import json

import faiss
import numpy as np
import pandas as pd
from answer_llm_hcx3 import answer_llm_stream
from embedding_query import embedding_query
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from numpy import dot
from numpy.linalg import norm
from pydantic import BaseModel

app = FastAPI()
segmentsQna = pd.read_pickle("server/docs/law_qna_v4.pkl")
# v4 = combined = answer + meta
# v5 = combined = answer + meta + contents
segmentsDocu = pd.read_pickle("server/docs/law_docu.pkl")
segmentsDocu = segmentsDocu.drop(index=55)

vectorsQna = np.array(segmentsQna["vector"].tolist()).astype(
    "float32"
)  # 벡터를 numpy 배열로 변환하고 float32 형식으로 변환
dimensionQna = vectorsQna.shape[1]  # 벡터 차원 계산

vectorsDocu = np.array(segmentsDocu["vector"].tolist()).astype(
    "float32"
)  # 벡터를 numpy 배열로 변환하고 float32 형식으로 변환
dimensionDocu = vectorsDocu.shape[1]  # 벡터 차원 계산

indexQna = faiss.IndexFlatL2(dimensionQna)  # Using L2 distance for similarity
indexQna.add(vectorsQna)

indexDocu = faiss.IndexFlatL2(dimensionDocu)  # Using L2 distance for similarity
indexDocu.add(vectorsDocu)


class Query(BaseModel):
    text: str


@app.post("/process_query/")
async def process_query(query: Query):
    print("Received query: " + query.text)
    query_emb = np.array(embedding_query(query.text)).astype(
        "float32"
    )  # 쿼리 임배딩 및 numpy 배열로 변환
    top_n = 1
    distancesQna, indicesQna = indexQna.search(
        query_emb.reshape(1, -1), top_n
    )  # Faiss유사한 벡터 찾기

    distancesDocu, indicesDocu = indexDocu.search(
        query_emb.reshape(1, -1), top_n
    )  # Faiss유사한 벡터 찾기

    firstSegmentQna = segmentsQna["vector"][indicesQna[0][0]]
    cosSimQna = dot(query_emb, firstSegmentQna) / (
        norm(query_emb) * norm(firstSegmentQna)
    )  # 수동으로 cosine 구하기
    print("qna cosine similarity: " + str(cosSimQna))

    firstSegmentDocu = segmentsDocu["vector"][indicesDocu[0][0]]
    cosSimDocu = dot(query_emb, firstSegmentDocu) / (
        norm(query_emb) * norm(firstSegmentDocu)
    )  # 수동으로 cosine 구하기
    print("docu cosine similarity: " + str(cosSimDocu))

    user_text = [query.text]

    relevantData = {}

    if cosSimQna >= 0.970 and cosSimDocu >= 0.970:  # 0.975넘으면 정보주기
        # Retrieve results
        top_segments = (
            "[정보]: "
            + " ".join(segmentsQna["Combined"][idx] for idx in indicesQna[0])
            + " ".join(segmentsDocu["Contents"][idx] for idx in indicesDocu[0])
        )
        user_text.insert(0, top_segments)
        relevantData = {
            "origin": [
                segmentsQna["answer"][indicesQna[0]].tolist(),
                segmentsDocu["Contents"][indicesDocu[0]].tolist(),
            ],
            "meta": [
                segmentsQna["Meta"][indicesQna[0]].tolist(),
                segmentsDocu["Meta"][indicesDocu[0]].tolist(),
            ],
            "cos_sim": [cosSimQna, cosSimDocu],
        }
    else:
        print("unrelated")
        relevantData = {
            "origin": [
                segmentsQna["answer"][indicesQna[0]].tolist(),
                segmentsDocu["Contents"][indicesDocu[0]].tolist(),
            ],
            "meta": [
                segmentsQna["Meta"][indicesQna[0]].tolist(),
                segmentsDocu["Meta"][indicesDocu[0]].tolist(),
            ],
            "cos_sim": [cosSimQna, cosSimDocu],
        }

    async def stream_response():
        async for line in answer_llm_stream("\n\n".join(user_text)):
            yield line.encode()
        # Stream relevantData
        yield "event:json\n".encode()
        yield ("data:" + json.dumps(relevantData)).encode()

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }

    return StreamingResponse(content=stream_response(), headers=headers)
