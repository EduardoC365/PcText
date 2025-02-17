import openai
import streamlit as st
from openai import AzureOpenAI
import json
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from openai import AzureOpenAI
from bson import ObjectId  # Importamos ObjectId para manejar el tipo especial de MongoDB

# Cargar las variables del .env
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
MONGO_URI = os.getenv("MONGO_URI")  # Asegúrate de que tienes la URI de tu MongoDB

# Configurar el cliente de OpenAI
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-08-01-preview",
)

# Configurar cliente de MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["box"]
productos_collection = db["productos"]

def convertir_objectid(obj):
    """Convierte ObjectId a string para hacer los datos serializables"""
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Tipo de objeto no serializable: {type(obj)}")

def generar_respuesta(prompt):
    """Llama a la API de Azure OpenAI y genera una respuesta basada en toda la colección de productos"""
    try:
        # Obtener todos los productos de la colección
        productos = productos_collection.find()

        # Convertir todos los productos obtenidos a JSON, convirtiendo ObjectId a string
        productos_texto = json.dumps([producto for producto in productos], default=convertir_objectid, ensure_ascii=False, indent=2)

        # Llamar al modelo de OpenAI con toda la información de los productos
        respuesta = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": "Eres un asistente de ordenadores, vas a consultar esta información: " + productos_texto},
                      {"role": "user", "content": prompt}],
        )

        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al llamar a la API o consultar la base de datos: {str(e)}"
def asistente(prompt):

    try:
        # Obtener todos los productos de la colección
        productos = productos_collection.find()

        # Convertir todos los productos obtenidos a JSON, convirtiendo ObjectId a string
        productos_texto = json.dumps([producto for producto in productos], default=convertir_objectid, ensure_ascii=False, indent=2)

        # Llamar al modelo de OpenAI con toda la información de los productos
        respuesta = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": "Te encargas de ser un asistente, tienes que hablar con el cliente para que compre un ordenador, con toque amigable y sinpatico. Si es necesario consulta la base de datos." + productos_texto},
                        {"role": "user", "content": prompt}],
        )

        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al llamar a la API o consultar la base de datos: {str(e)}"
