import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
# Se encarga de meter los datos del JSON 
# Cargar las variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")  # La URL de conexión a MongoDB Atlas
 
# Cargar el JSON que deseas subir (puedes usar el archivo 'results.json' que generaste)
with open("../productos.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
 
# Conectar a MongoDB Atlas
client = MongoClient(MONGO_URI)
 
# Seleccionar la base de datos y colección
db = client["dudu-shop"]  # Reemplaza con el nombre de tu base de datos
collection = db["dudu-components"]  # Reemplaza con el nombre de tu colección
 
# Insertar los documentos del JSON en la colección
if isinstance(data, list):
    collection.insert_many(data)  # Insertar varios documentos
else:
    collection.insert_one(data)  # Insertar un único documento
 
print("Documentos cargados a MongoDB Atlas exitosamente.")