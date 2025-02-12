from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os

# Configuración
endpoint = "https://documentreaderpdf.cognitiveservices.azure.com/"
key = "3ZLnKUYwabFD71VIzmcY5mdCwZYLjObjg3WkbvSqTXC3GZQjnt2IJQQJ99BBACYeBjFXJ3w3AAALACOGuEoF"
document_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))

# Carpeta con los PDFs
pdf_folder = "./pdfs"
output_folder = "./textextract"
os.makedirs(output_folder, exist_ok=True)

# Procesar cada PDF
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        with open(pdf_path, "rb") as pdf_file:
            poller = document_client.begin_analyze_document("prebuilt-read", document=pdf_file)
            result = poller.result()

        # Extraer texto y guardarlo en un TXT
        extracted_text = "\n".join([line.content for page in result.pages for line in page.lines])
        txt_filename = os.path.join(output_folder, f"{filename}.txt")
        
        with open(txt_filename, "w", encoding="utf-8") as txt_file:
            txt_file.write(extracted_text)

        print(f"Texto extraído y guardado en {txt_filename}")
