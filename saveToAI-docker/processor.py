import os
from typing import List, Optional
from dotenv import load_dotenv
import trafilatura
from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from CachedChroma import (CachedChroma)
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from documentdb import MyMongoDB

def get_text_splitter(recursive: bool = True):
    if recursive:
        return RecursiveCharacterTextSplitter(chunk_size=1386, chunk_overlap=80, add_start_index=True)
    else:
        return CharacterTextSplitter(separator="\n", chunk_size=1386, chunk_overlap=80, add_start_index=True)


class Processor:
    def __init__(self):
        # find mongo singleton
        self.mongo = MyMongoDB()

        load_dotenv("./.env")
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.openai_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    def create_or_get_embedding_store(self, collection_name: str) -> Chroma:
        vectorstore = CachedChroma.from_documents_with_cache(
            persist_directory="chroma_db/.",
            documents=[],
            embedding=self.openai_embeddings,
            collection_name=collection_name
        )
        return vectorstore

    @classmethod
    def chunk_and_split_one(cls, text: str, recursive=True) -> List[str]:
        docs = get_text_splitter(recursive).split_text(text)
        return docs

    @classmethod
    def chunk_and_split(cls, documents: List[Document], recursive=True) -> List[Document]:
        docs = get_text_splitter(recursive).split_documents(documents)
        return docs
    

    def save_web_content_no_vectorize(self, collection_name: str, url: str) -> None:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        if len(text) < 50 and "javascript" in text.lower():
            # raise Exception("Javascript page detected")
            print(f"Javascript page detected.. Skipping {url}")
        mongo = MyMongoDB()
        mongo.save_text_content_to_mongo(collection_name, text, url)
        return

    def save_web_content_to_chromadb(self, collection_name: str, url: str) -> None:
        chroma = self.create_or_get_embedding_store(collection_name)
        downloaded = trafilatura.fetch_url(url)
        # it can silently grab an empty "you need javascript" page
        text = trafilatura.extract(downloaded)
        if len(text) < 50 and "javascript" in text.lower():
            # raise Exception("Javascript page detected")
            print(f"Javascript page detected.. Skipping {url}")
        split_docs = Processor.chunk_and_split_one(text, recursive=False)
        metadata_list = [{"url": url, "part": index} for index in range(len(split_docs))]
        # for split_doc in split_docs:
        #     print("adding text:=============")
        #     print(split_doc)
        #     print("=============")
        chroma.add_texts(texts=split_docs, metadatas=metadata_list)
        return 

    def process_youtube(self, collection_name: str, video_id: str, transcript: str, metadata: dict) -> None:
        print("collection: " + collection_name)
        print("video_id: " + video_id)
        print("transcript: " + transcript[:200])
        # print("metadata: " + metadata)
        self.mongo.save_youtube_transcript(collection_name, video_id, transcript, metadata)

    """processes document. If  returns metadata"""
    def process_document(self, collection_name: str, documents: List[Document]) -> dict:
        chroma = self.create_or_get_embedding_store(collection_name)

        docs_already_in_db = chroma.get(where={"source": documents[0].metadata["source"]})
        if len(docs_already_in_db['documents']):
            split_docs = Processor.chunk_and_split(documents)
            chroma.add_documents(split_docs)
        else:
            print("Skipping video " + documents[0].metadata["source"])
        return documents[0].metadata

    def save_text_no_vectorize(self, collection_name, text, source):
        mongo = MyMongoDB()
        mongo.save_text_content_to_mongo(collection_name, text, source)
        return

    def save_text_content_to_chromadb(self, collection_name: str, text: str, source: str) -> None:
        chroma = self.create_or_get_embedding_store(collection_name)
        split_docs = Processor.chunk_and_split_one(text, recursive=False)
        metadata_list = [{"source": source, "part": index} for index in range(len(split_docs))]
        chroma.add_texts(texts=split_docs, metadatas=metadata_list)

    def query_page(self, collection_name: str, questions: List[str]) -> Chroma:
        index = self.create_or_get_embedding_store(collection_name)
        for question in questions:
            print(f"Question: {question}\n")
            docs = index.similarity_search(question)
            print(f"Answer: {index.similarity_search(question)}\n")
        return index
