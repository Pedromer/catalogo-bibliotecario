# Catálogo Online de Libros

Sistema de gestión de catálogo online desarrollado con Django, diseñado para administrar el registro de libros físicos y digitales para un catalogo visual y accesible.

##  Características Principales

*   **Insercion de portadas y contraportadas a cada libro:** Este proyecto busca tener un caracter visual para una biblioteca escolar. A pedido del personal bibliotecario, esta caracteristica es fundamental.
*   **Exportacion e importacion de datos en cvs/lxsl:** En busca de ser una aplicacion que acompaña a los sistemas de gestion bibliotecaria como KOHA, es fundamental contar con herramientas de importacion de datos. Ademas, la exportacion del catalogo permite el seguimiento y peritaje del mismo siempre que sea necesario tanto para bibliotecarios como directivos de las instituciones.
*   **Interfaz pública:** Interfaz de usuario publica, sin inicio de sesion y maquetada para la buena visualizacion en cualquier dispositivo.

## Herramientas utilizadas

*   **Lenguaje & framework:** Python 3.x / Django
*   **Base de datos:** PostgreSQL/SQLite (dev)
*   **Almacenamiento multimedia:** Cloudinary
*   **Frontend:** HTML5, CSS3, Bootstrap
*   **Plataforma de despliegue optimizada:** Vercel 

## Roadmap (Próximas Mejoras)

*   Automatización completa de recolección de metadatos a partir del ingreso del código ISBN.
*   Motor de búsqueda avanzada con filtrado multicriterio y peticion veloz.

## Instalación y configuración local

Este proyecto ha sido desarrollado integramente en sistemas GNU/Linux y no se ha probado su funcionamiento en sistemas operativos Windows ni MACOS para su desarrollo.

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Pedromer/catalogo-bibliotecario
   cd catalogo-bibliotecario
   ```

2. Crear y activar el entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Instalar las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

4. En caso de querer utilizar Cloudinary/Supabase y no querer usar SQLite: configurar las variables de entorno. Crear un archivo `.env` en la raíz del proyecto y agregar las siguientes credenciales:
   ```env
   # Django
   SECRET_KEY=tu_secret_key_aqui
   DEBUG=True

   # Supabase (PostgreSQL)
   DATABASE_URL=postgres://usuario:password@host:puerto/dbname

   # Cloudinary
   CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
   ```

5. Aplicar las migraciones para inicializar la base de datos:
   ```bash
   python manage.py migrate
   ```

6. Crear un superusuario para acceder al panel de administración:
   ```bash
   python manage.py createsuperuser
   ```

7. Iniciar el servidor de desarrollo local:
   ```bash
   python manage.py runserver
   ```
   El proyecto estará disponible en `http://localhost:8000/`.
