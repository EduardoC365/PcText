import streamlit as st
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from pymongo import MongoClient

st.set_page_config(page_title='DuduShop', layout='wide')

def get_language_service_client(endpoint: str, key: str):
    return ConversationAnalysisClient(endpoint, AzureKeyCredential(key))

def get_mongo_client(uri: str):
    return MongoClient(uri)

def load_configuration():
    load_dotenv()
    return os.getenv('LS_CONVERSATIONS_ENDPOINT'), os.getenv('LS_CONVERSATIONS_KEY'), os.getenv('MONGO_URI')

def analyze_conversation(client, query, project='PcShop', deployment='dududespliegue'):
    try:
        with client:
            return client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "participantId": "1",
                            "id": "1",
                            "modality": "text",
                            "language": "en",
                            "text": query
                        },
                        "isLoggingEnabled": False
                    },
                    "parameters": {
                        "projectName": project,
                        "deploymentName": deployment,
                        "verbose": True
                    }
                }
            )
    except Exception as e:
        return {"error": str(e)}

def get_catalog_from_db(mongo_client):
    db = mongo_client['dudu-shop']
    collection = db['dudu-components']
    return list(collection.find())

def get_product_names_and_prices_from_db(mongo_client):
    db = mongo_client['dudu-shop']
    collection = db['dudu-components']
    return [{"NombreProducto": item.get('NombreProducto', 'Producto sin nombre'), "Precio": item.get('Precio', 'No disponible')} for item in collection.find()]

def main():
    st.title("DuduShop - Asistente de compras")
    endpoint, key, mongo_uri = load_configuration()
    client = get_language_service_client(endpoint, key)
    mongo_client = get_mongo_client(mongo_uri)

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container()
    with chat_container:
        st.write("### Chat con el Asistente")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["text"])

    user_input = st.chat_input("Escribe tu mensaje...")

    if user_input:
        st.session_state.messages.append({"role": "user", "text": user_input})
        result = analyze_conversation(client, user_input)

        if "error" in result:
            response = f"❌ Error en la consulta: {result['error']}"
        else:
            prediction = result["result"]["prediction"]
            top_intent = prediction["topIntent"]

            if top_intent == "Curiosidad":
                response = "Aquí tienes nuestro catálogo:"
                st.session_state.catalog = get_catalog_from_db(mongo_client)
            elif top_intent == "Comprar":
                response = "Si quieres comprar un producto, por favor dinos SOLO el nombre del producto."
            else:
                response = "No entendí tu solicitud."

        st.session_state.messages.append({"role": "assistant", "text": response})
        st.rerun()

    if 'catalog' in st.session_state:
        with st.sidebar:
            st.write("### Catálogo de Productos")
            for item in st.session_state.catalog:
                st.markdown(f"**{item.get('NombreProducto', 'Producto sin nombre')}**")
                for k, v in item.items():
                    if k != '_id':
                        st.text(f"{k}: {v}")
                st.markdown("---")

    with st.sidebar:
        st.write("### Opciones Rápidas")
        if st.button("Ver Catálogo de Productos"):
            st.session_state.catalog = get_catalog_from_db(mongo_client)
            st.write("### Catálogo de Productos")
            for item in st.session_state.catalog:
                st.markdown(f"**{item.get('NombreProducto', 'Producto sin nombre')}**")
                for k, v in item.items():
                    if k != '_id':
                        st.text(f"{k}: {v}")
                st.markdown("---")
        
        if st.button("Ver Precio de los Productos"):
            st.session_state.product_prices = get_product_names_and_prices_from_db(mongo_client)
            st.write("### Precios de los Productos")
            for item in st.session_state.product_prices:
                st.markdown(f"**{item.get('NombreProducto', 'Producto sin nombre')}** - **Precio:** {item.get('Precio', 'No disponible')}")
            st.markdown("---")

        st.write("### Respuesta del Modelo")
        if st.session_state.messages:
            st.markdown(st.session_state.messages[-1]["text"])

        if st.button("🔄 Refrescar Conversación"):
            st.session_state.messages = []
            if 'catalog' in st.session_state:
                del st.session_state.catalog
            if 'product_prices' in st.session_state:
                del st.session_state.product_prices
            st.rerun()

if __name__ == "__main__":
    main()
