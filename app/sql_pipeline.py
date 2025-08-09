from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from app.settings import get_db_url, GOOGLE_API_KEY

class SQLPipeline:
    def __init__(self):
        self.agents = {}

    def get_llm(self, llm_choice: str):
        if llm_choice == "gemini":
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)
        return OllamaLLM(model="gemma3:12b", temperature=0)

    def ask(self, query: str, db_name: str, llm_choice: str):
        key = f"{db_name}_{llm_choice}"
        if key not in self.agents:
            db = SQLDatabase.from_uri(get_db_url(db_name))
            llm = self.get_llm(llm_choice)
            # Few-shot para fidelidad en CMMS queries
            agent = create_sql_agent(
                llm=llm, db=db, verbose=True, max_iterations=10,
                agent_executor_kwargs={"handle_parsing_errors": True},
                prefix="Eres un agente SQL preciso para CMMS. Usa joins correctos y limita resultados. Output raw JSON si posible."
            )
            self.agents[key] = agent
        response = self.agents[key].invoke({"input": query})
        return response.get("output", "Error en consulta")