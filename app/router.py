from langchain_ollama import OllamaLLM
import json

class Router:
    def __init__(self):
        self.llm = OllamaLLM(model="gemma3:12b", temperature=0)
        with open("chroma_db/metadata.json", "r") as f:
            self.summaries = json.load(f)

    def choose_sources(self, question: str):
        tools_desc = "\n".join([f"- {name}: {data['summary']}" for name, data in self.summaries.items()])
        prompt = f"""
        Basado en la pregunta: "{question}"
        Elige fuentes relevantes de: {tools_desc}
        También considera DBs como atlas_cmms si menciona datos dinámicos.
        Responde con nombres separados por comas (e.g., 'doc1,atlas_cmms').
        """
        return self.llm.invoke(prompt).strip().split(',')