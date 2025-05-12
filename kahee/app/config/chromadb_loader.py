## CHROMA DB 관련 설정

# 라이브러리 및 설정 가져오기
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config.settings import settings

# 임베딩 함수
embeddings = OpenAIEmbeddings()

# VectorStore
vectorstore = Chroma(
    collection_name=settings.COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=settings.CHROMA_DIR,
)

collection = vectorstore._collection