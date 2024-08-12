import streamlit as st
from pymongo import MongoClient
from bson.binary import Binary
import pandas as pd
from io import BytesIO
import os

def descargar_pdf(client, database_name, collection_name, numero_presupuesto):
    """Descargar el PDF desde MongoDB basado en el número de presupuesto."""
    db = client[database_name]
    collection = db[collection_name]

    # Buscar el documento que contiene el número de presupuesto
    documento = collection.find_one({"numero_factura": numero_presupuesto})

    if documento and "pdf" in documento:
        pdf_bytes = documento["pdf"]
        return pdf_bytes
    else:
        return None

def obtener_toda_la_base_datos(client, database_name, collection_name):
    """Obtener toda la base de datos y retornarla como un DataFrame de pandas."""
    db = client[database_name]
    collection = db[collection_name]

    # Obtener todos los documentos de la colección
    documentos = collection.find()

    # Convertir a DataFrame de pandas
    df = pd.DataFrame(documentos)

    # Eliminar la columna '_id' si existe, para que no haya problemas con Excel
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # Añadir una columna 'PDF Existente' para indicar si hay un PDF
    df['PDF Existente'] = df['pdf'].apply(lambda x: 'Sí' if x is not None else 'No')

    # Eliminar la columna 'pdf' para que no se exporte
    df = df.drop(columns=['pdf'])

    return df

def main():
    # Conexión a MongoDB
    uri = "mongodb+srv://cjhd92:cesar123@cluster0.cuuq5et.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri)

    # Especificar la base de datos y la colección
    database_name = "db_pastelera"
    collection_name = "shows"

    st.title("Aplicación de Gestión de Documentos")

    # Entrada para el número de presupuesto
    numero_presupuesto = st.text_input("Ingrese el número de presupuesto:")

    # Botón para descargar el PDF
    if st.button("Descargar PDF"):
        if numero_presupuesto:
            pdf_bytes = descargar_pdf(client, database_name, collection_name, numero_presupuesto)
            if pdf_bytes:
                st.success(f"PDF para el presupuesto {numero_presupuesto} encontrado.")
                st.download_button(
                    label="Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"presupuesto_{numero_presupuesto}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("No se encontró el PDF para el número de presupuesto especificado.")
        else:
            st.warning("Por favor, ingrese un número de presupuesto válido.")

    # Botón para descargar el Excel
    if st.button("Descargar toda la base de datos como Excel"):
        df = obtener_toda_la_base_datos(client, database_name, collection_name)
        if not df.empty:
            # Convertir el DataFrame a un archivo Excel en memoria
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Datos')
            st.success("Base de datos exportada exitosamente.")
            st.download_button(
                label="Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name="base_de_datos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No hay datos disponibles para exportar.")

if __name__ == "__main__":
    main()
