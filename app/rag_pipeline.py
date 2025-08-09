import json
import os
import logging
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from app.settings import EMBEDDING_MODEL, PERSIST_DIRECTORY, GOOGLE_API_KEY
import torch

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SmartRAG:
    def __init__(self):
        self.embed_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True, 'batch_size': 32}
        )
        self.metadata_path = os.path.join(PERSIST_DIRECTORY, 'metadata.json')
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        except FileNotFoundError:
            logger.error("No se encontró metadata.json")
            self.metadata = {}

    def get_llm(self, llm_choice: str):
        logger.debug(f"Seleccionando LLM: {llm_choice}")
        if llm_choice == "gemini":
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)
        return OllamaLLM(model="gemma3:12b", temperature=0.2)  # Temperatura para ayudar a encontrar datos

    def query(self, question: str, collection_name: str, llm_choice: str):
        logger.debug(f"Procesando consulta: {question} en colección: {collection_name} con LLM: {llm_choice}")
        print(f"Usando GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
        llm = self.get_llm(llm_choice)
        try:
            vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embed_model, collection_name=collection_name)
        except Exception as e:
            logger.error(f"Error al cargar vectorstore para {collection_name}: {str(e)}")
            raise
        # Retrieval avanzado: Aumentar para más documentos, ayudando a Gemma
        base_retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 45, 'fetch_k': 110})
        compressor = LLMChainExtractor.from_llm(llm)
        retriever = ContextualCompressionRetriever(base_retriever=base_retriever, base_compressor=compressor)

        # Prompt mejorado: Razonamiento paso a paso para Gemma
        qa_template = """
        Analiza el contexto paso a paso:
        1. Identifica info relevante para la pregunta.
        2. Cita verbatim del contexto.
        3. Menciona fuente/página.
        Usa SOLO el contexto proporcionado. Si no hay info relevante, responde "No encontrado".
        Contexto: {context}
        Pregunta: {question}
        Respuesta concisa:
        """
        qa_prompt = PromptTemplate.from_template(qa_template)

        # Usar "stuff" con verbose para depuración
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": qa_prompt},
            verbose=True  # Para ver proceso interno con Gemma
        )
        response = qa_chain.invoke({"query": question})
        logger.debug(f"Respuesta generada: {response['result']}")
        return response['result']