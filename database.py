from pymongo import MongoClient

# Conectar ao MongoDB (localhost)
MONGO_URI = "mongodb://localhost:27017"  # Conexão local
DB_NAME = "_Users_"  # Nome da sua database

def get_database():
    """Retorna a instância do banco de dados MongoDB."""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def get_users_collection():
    """Retorna a coleção de usuários dentro do banco de dados."""
    db = get_database()
    return db["Fluffy_Chips_Web_Analiser"]  # Nome correto da coleção
