# HDT4 - Sistema RAG con PostgreSQL, pgvector y LLM Tool Calling
**Universidad del Valle de Guatemala**  
**Autor:** Pedro Caso - 241286  

Este proyecto implementa una solución de Recuperación Aumentada por Generación (RAG, por sus siglas en inglés) para la empresa Parachute S.A. Se utiliza PostgreSQL con la extensión pgvector como base de datos vectorial para el almacenamiento de embeddings, sentence-transformers con el modelo local `all-MiniLM-L6-v2` para la generación de vectores semánticos, y un agente interactivo por consola que aprovecha el mecanismo de Tool Calling (Function Calling) mediante el SDK de OpenAI conectado a la API de NVIDIA.

---

## Video demostrativo:

[![Video demostrativo](https://img.youtube.com/vi/Pa21BObDQwc/hqdefault.jpg)](https://youtu.be/Pa21BObDQwc

---

## Estructura del Proyecto

* **docker-compose.yml**: Definición del servicio de base de datos PostgreSQL con la extensión oficial pgvector (imagen `pgvector/pgvector:pg16`).
* **db.py**: Módulo encargado de gestionar la conexión con PostgreSQL, inicializar la extensión vectorial y la tabla de datos, e implementar la búsqueda por similitud de coseno.
* **load.py**: Script de ingesta que procesa el corpus de preguntas frecuentes, genera las representaciones vectoriales locales y las inserta en la base de datos.
* **agent.py**: Programa principal del agente conversacional. Implementa el bucle interactivo de terminal y el manejo de llamadas a herramientas (Tool Calling).
* **data/Corpus_FAQs_Parachute_SA_2026.txt**: Fuente oficial de datos estructurados con 120 preguntas frecuentes y metadatos del evento de paracaidismo.
* **requeriments.txt**: Lista de dependencias del proyecto para su instalación en el entorno virtual.
* **.env.example**: Plantilla de variables de entorno requeridas para la ejecución.

- _Se entregan los dos programas requeridos: load.py (carga) y agent.py (agente conversacional), apoyados por el módulo db.py para la gestión modular de la base de datos_

---

## Archivos y Directorios Excluidos de Versionamiento

Para mantener la seguridad del sistema y evitar la subida de binarios o credenciales al repositorio, los siguientes elementos están configurados en el archivo `.gitignore`:

1. **.env**: Contiene credenciales sensibles, incluyendo la clave de acceso a la API del modelo de lenguaje y contraseñas de la base de datos.
2. **postgres_data/ y pgdata/**: Directorios locales de persistencia de Docker en caso de utilizar montajes directos. Subir estos directorios genera problemas de concurrencia, permisos y corrupción de datos binarios entre diferentes sistemas operativos.
3. **.venv/, venv/, env/**: Entornos virtuales de Python. Las librerías deben ser instaladas localmente por cada usuario a partir de `requeriments.txt`.
4. **__pycache__/ y *.pyc**: Archivos de bytecode generados automáticamente por el intérprete de Python.

---

## Requisitos Previos

* Docker Desktop o Podman en ejecución.
* Python 3.10 o superior (probado en Python 3.11).
* Clave de API válida para la plataforma de inferencia de NVIDIA (NVIDIA NIM).

---

## Guía de Inicialización de Infraestructura

Para poner en marcha el proyecto desde cero, siga los pasos descritos a continuación:

### 1. Iniciar la Base de Datos Vectorial
Ejecute en la raíz del proyecto para crear y levantar el contenedor de PostgreSQL con soporte vectorial:
```bash
docker compose up -d
```
Puede verificar que el contenedor se encuentre activo ejecutando:
```bash
docker ps
```
El contenedor `parachute_pgvector` deberá estar en estado activo y escuchando en el puerto 5432.

### 2. Configurar el Entorno Virtual de Python
Cree y active un entorno virtual aislado para instalar los paquetes necesarios:

En Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requeriments.txt
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requeriments.txt
```

### 3. Configurar Variables de Entorno
Genere el archivo de configuración local a partir de la plantilla:
```bash
cp .env.example .env
```
Edite el archivo `.env` resultante e ingrese su clave de API y los parámetros de conexión:
```env
NVIDIA_API_KEY=su_clave_aqui
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=deepseek-ai/deepseek-v4-flash-0731

DB_HOST=localhost
DB_PORT=5432
DB_NAME=parachuteDB
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## Carga de la Base de Conocimientos

Antes de interactuar con el agente por primera vez, es necesario indexar el documento de preguntas frecuentes:
```bash
python load.py
```
Este script realiza las siguientes operaciones:
1. Lee y analiza las 120 fichas estructuradas de `data/Corpus_FAQs_Parachute_SA_2026.txt`.
2. Descarga y carga en memoria el modelo `all-MiniLM-L6-v2`.
3. Calcula los vectores de incrustación (embeddings) de 384 dimensiones para cada pregunta y respuesta.
4. Inicializa la extensión `vector` y la tabla `faqs` en PostgreSQL.
5. Inserta los registros y vectores en la base de datos.

---

## Ejecución del Agente Conversacional

Una vez completada la carga de datos, inicie el agente interactivo:
```bash
python agent.py
```

### Características del Agente:
* **Tool Calling con el SDK:** El agente no tiene el texto completo inyectado en su contexto inicial. Cuando el usuario realiza una consulta sobre el evento o las políticas de Parachute S.A., el modelo decide invocar la función `consultar_base_conocimientos` para buscar semánticamente las respuestas más relevantes en PostgreSQL.
* **Restricción estricta de dominio:** El sistema está configurado para responder exclusivamente con la información verificada obtenida de la base de datos. Si una pregunta hace referencia a temas ajenos o no contemplados en el documento oficial, el agente indica cortésmente que no cuenta con esa información y refiere al correo de atención oficial (`soporte@parachutesa.gt`).
* **Sesión interactiva continua:** Permite realizar múltiples preguntas de forma consecutiva dentro de la misma sesión.
* **Cierre de sesión:** Para salir del programa, escriba `bye` o utilice la combinación de teclas `Ctrl + C`.

---

## Detener la Infraestructura

Para suspender la ejecución del contenedor de base de datos sin perder los datos indexados:
```bash
docker compose down
```
Los datos permanecerán resguardados en el volumen administrado por Docker para posteriores ejecuciones.
