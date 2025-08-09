import os
import glob
import json
import re
from langchain_unstructured import UnstructuredLoader
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
import pandas as pd
from app.settings import EMBEDDING_MODEL, PERSIST_DIRECTORY

def sanitize_collection_name(filename: str) -> str:
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    return name

def ingest_data():
    source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'source')
    files = glob.glob(os.path.join(source_dir, '*.*'))  # PDFs, Excels, TXT, etc.
    
    if not files:
        print("No se encontraron archivos en 'source'.")
        return
    
    embed_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    semantic_splitter = SemanticChunker(embed_model)
    
    collections_metadata = {}
    
    for file_path in files:
        collection_name = sanitize_collection_name(file_path)
        print(f"Procesando: {file_path} -> {collection_name}")
        
        docs = []
        try:
            if file_path.lower().endswith('.pdf'):
                loader = UnstructuredLoader(file_path, mode="elements", languages=["spa"])  # Especificar español
                raw_docs = loader.load()
                for i, doc in enumerate(raw_docs):
                    doc.metadata['source'] = file_path
                    doc.metadata['page'] = doc.metadata.get('page_number', i + 1)
                chunks = semantic_splitter.split_documents(raw_docs)
                docs.extend(chunks)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                xl = pd.ExcelFile(file_path)
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    markdown_table = df.to_markdown(index=False)
                    doc = text_splitter.create_documents([markdown_table])[0]
                    doc.metadata = {'source': file_path, 'sheet': sheet}
                    docs.append(doc)
            elif file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                chunks = text_splitter.create_documents([text])
                for chunk in chunks:
                    chunk.metadata = {'source': file_path}
                docs.extend(chunks)
            else:
                print(f"Ignorando archivo no soportado: {file_path}")
                continue
            
            if docs:
                Chroma.from_documents(docs, embed_model, persist_directory=PERSIST_DIRECTORY, collection_name=collection_name)
                summary = "Resumen corto del documento."  # Agrega lógica para resúmenes si deseas
                collections_metadata[collection_name] = {"summary": summary}
            else:
                print(f"No se generaron documentos para: {file_path}")
        
        except Exception as e:
            print(f"Error procesando {file_path}: {str(e)}")
            continue
    
    metadata_path = os.path.join(PERSIST_DIRECTORY, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(collections_metadata, f, ensure_ascii=False, indent=4)
    
    print("\n¡Ingesta completada!")

if __name__ == "__main__":
    ingest_data()