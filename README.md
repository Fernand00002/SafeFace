# SafeFace · Búsqueda Humanitaria

Prototipo web desarrollado en Python que facilita la localización de personas desaparecidas mediante reconocimiento facial biométrico y comparación vectorial en la nube.

## Tecnologías Utilizadas
* **Python 3.10+**
* **Streamlit** (Interfaz web interactiva)
* **OpenCV** & **face_recognition** (Procesamiento y extracción de vectores faciales de 128 dimensiones)
* **Supabase** (Base de datos PostgreSQL, extensión `pgvector` y almacenamiento en la nube)

## Integrantes
* **Diego Fernando Pérez Castillo N°28
* **Brandon Isaac Campos Valle N°16

## Características Principales
* **Registro Biométrico:** Ingreso de fichas con datos personales y fotografía para análisis vectorial automático.
* **Búsqueda por Similitud:** Comparación de rostros mediante consulta RPC con `pgvector` en Supabase.
* **Panel Administrativo:** Módulo seguro protegido por credenciales para supervisar los registros activos.

## Configuración y Ejecución Local
1. Clona este repositorio.
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
