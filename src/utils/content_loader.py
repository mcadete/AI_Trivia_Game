from typing import List, Optional
from langchain_community.document_loaders import (
    WebBaseLoader,
    GitHubRepositoryLoader,
    PyPDFLoader,
    BSHTMLLoader
)
from langchain_community.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import chromadb
import os

class ContentLoader:
    def __init__(self, persist_directory: str = ".chromadb"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize ChromaDB
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    def load_web_content(self, urls: List[str]) -> None:
        """Load content from web pages"""
        loader = WebBaseLoader(urls)
        docs = loader.load()
        splits = self.text_splitter.split_documents(docs)
        self.vectorstore.add_documents(splits)
    
    def load_github_content(
        self,
        repo_url: str,
        branch: str = "main",
        file_filter: Optional[List[str]] = None
    ) -> None:
        """Load content from GitHub repository"""
        loader = GitHubRepositoryLoader(
            clone_url=repo_url,
            branch=branch,
            file_filter=file_filter or [".md", ".txt", ".py", ".js", ".html"]
        )
        docs = loader.load()
        splits = self.text_splitter.split_documents(docs)
        self.vectorstore.add_documents(splits)
    
    def load_pdf_content(self, pdf_paths: List[str]) -> None:
        """Load content from PDF files"""
        for path in pdf_paths:
            if os.path.exists(path):
                loader = PyPDFLoader(path)
                docs = loader.load()
                splits = self.text_splitter.split_documents(docs)
                self.vectorstore.add_documents(splits)
    
    def load_html_content(self, html_paths: List[str]) -> None:
        """Load content from HTML files"""
        for path in html_paths:
            if os.path.exists(path):
                loader = BSHTMLLoader(path)
                docs = loader.load()
                splits = self.text_splitter.split_documents(docs)
                self.vectorstore.add_documents(splits)
    
    def search_content(
        self,
        query: str,
        n_results: int = 5
    ) -> List[dict]:
        """Search for relevant content in the vector store"""
        results = self.vectorstore.similarity_search(
            query,
            k=n_results
        )
        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "score": doc.metadata.get("score", 0)
            }
            for doc in results
        ] 