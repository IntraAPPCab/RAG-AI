import os

EMBEDDING_MODEL = "intfloat/e5-large"  # Mejor para fidelidad en textos técnicos
PERSIST_DIRECTORY = "chroma_db"
GOOGLE_API_KEY = "AIzaSyCcT_I3oxYWwWMftMxk3UhF1obaUPxrFSk"  # Tu key

DATABASES = {
    "atlas_cmms": {
        "user": "rootUser",
        "password": "mypassword",
        "host": "localhost",
        "port": "5432",
        "db_name": "atlas"
    },
    # Agrega más DBs si necesitas (e.g., Tango/Chess si exportan a Postgres)
}

def get_db_url(db_name: str) -> str:
    db_info = DATABASES.get(db_name)
    if db_info:
        return f"postgresql+psycopg2://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/{db_info['db_name']}"
    return None