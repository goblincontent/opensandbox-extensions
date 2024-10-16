from abc import ABC
from typing import List, Optional, Any
from langchain.docstore.document import Document
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb


class CachedChroma(Chroma, ABC):
    """Wrapper around chroma to make caching embeddings easier
        Example usage:
        from langchain.vectorstores import Chroma
        from langchain.embeddings.openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings()
        vectorstore = CachedChroma.from_documents_with_cache(
        persist_directory=".",
        texts,
        embeddings,
        collection_name="my_collection"
        )
    """
    @classmethod
    def from_documents_with_cache(
            cls,
            persist_directory: str,
            documents: List[Document],
            embedding: Optional[OpenAIEmbeddings] = OpenAIEmbeddings,
            ids: Optional[List[str]] = None,
            collection_name: str = Chroma._LANGCHAIN_DEFAULT_COLLECTION_NAME,
            client_settings: Optional[chromadb.config.Settings] = None,
            **kwargs: Any,
    ) -> Chroma:
        client = chromadb.PersistentClient(path=persist_directory)
        collection_names = [c.name for c in client.list_collections()]

        if collection_name in collection_names:
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding,
                persist_directory=persist_directory,
                client_settings=client_settings,
            )

        return Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            ids=ids,
            collection_name=collection_name,
            persist_directory=persist_directory,
            client_settings=client_settings,
        )

