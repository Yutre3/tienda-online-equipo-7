# Tienda en línea - Equipo 7

Proyecto modular de Programación Orientada a Objetos en Python. El sistema
administra clientes, productos, existencias, pedidos y detalles de pedido de una
tienda en línea.

La organización sigue la forma de trabajo del profesor en
[IEC_N2_C1_POO](https://github.com/baileytorch/IEC_N2_C1_POO): presentación,
negocio, datos, archivos auxiliares y SQL separados. El contenido y las reglas
corresponden únicamente al tema del Equipo 7.

## Estructura

```text
TI3021_U2_EF01/
├── .vscode/                 Configuración compartida de Visual Studio Code
├── auxiliares/              Nombre y opciones del menú
├── datos/
│   ├── sql/                 Esquema permanente y versionado de MariaDB
│   └── models.py            Clases, conexión y persistencia
├── negocio/                 Reglas y servicios de la tienda
├── presentacion/            Menú de consola
├── .env.example             Plantilla de conexión sin datos personales
├── .gitignore               Archivos que Git no debe publicar
├── app.py                   Punto de entrada
├── requirements.txt         Dependencias de Python
└── README.md
```

La base permanente se llama `tienda_online` y contiene estas tablas:
`clientes`, `productos`, `pedidos` y `detalles_pedido`. Sus relaciones, índices
y restricciones están en
`datos/sql/2026.10.05_20.00_DDL_Tienda_Online.sql`.

## Programas necesarios

- Python 3.10 o superior.
- Visual Studio Code con la extensión oficial de Python.
- XAMPP con MySQL/MariaDB iniciado.
- Git.

Visual Studio Code recomendará además las extensiones necesarias para Python y
para consultar MySQL. No se usan rutas absolutas ni archivos propios de un solo
computador.

## Preparación después de clonar

Clone y entre al repositorio:

```bash
git clone https://github.com/Yutre3/tienda-online-equipo-7.git
cd tienda-online-equipo-7
```

Abra esa carpeta en Visual Studio Code mediante **Archivo > Abrir carpeta**. El
explorador quedará ordenado como en la referencia del profesor. También puede
abrirla desde una terminal con:

```bash
code .
```

En Windows PowerShell, cree el entorno e instale las dependencias:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Configuración de la base permanente

1. Abra XAMPP e inicie **MySQL**.
2. Revise el archivo `.env` creado desde la plantilla.
3. Ejecute `python app.py` desde la raíz del proyecto.

La configuración predeterminada de XAMPP es:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tienda_online
DB_USER=root
DB_PASSWORD=
```

Si el computador usa otro puerto, usuario o contraseña, cambie solamente el
valor correspondiente en `.env`. Este archivo es local y Git no lo publica.
La conexión opcional **Tienda Online (XAMPP)** de SQLTools usa los valores
predeterminados; si necesita otras credenciales, configúrelas localmente desde
la extensión y no guarde la contraseña en Git.

Al iniciar, la aplicación se conecta a MariaDB, crea permanentemente la base
`tienda_online` si todavía no existe, aplica el esquema SQL y muestra el mensaje
`Conexión exitosa`. El mismo esquema también se puede importar manualmente desde
phpMyAdmin. No se debe publicar la carpeta interna de datos de XAMPP: el archivo
SQL versionado es el respaldo reproducible que permite construir la misma base
en cualquier computador.

## Ejecutar y modificar

Con el entorno activado y MySQL iniciado:

```bash
python app.py
```

El menú permite registrar clientes y productos, crear pedidos, agregar productos
a un pedido y consultar lo almacenado. Los cambios se realizan según la capa:

- interfaz y mensajes: `presentacion/` y `auxiliares/`;
- reglas de la tienda: `negocio/`;
- clases, consultas o conexión: `datos/models.py`;
- cambios de tablas: un archivo SQL dentro de `datos/sql/`.

Visual Studio Code incluye la configuración **Ejecutar tienda en línea** en la
sección **Ejecutar y depurar**. El archivo `.vscode/settings.json` usa siempre el
entorno `.venv` situado dentro del proyecto.

## Trabajo grupal con Git y GitHub

Antes de comenzar una tarea:

```bash
git switch main
git pull origin main
git switch -c nombre-de-la-tarea
```

Para guardar y compartir cambios:

```bash
git status
git add archivo_modificado.py
git commit -m "Descripción clara del cambio"
git push -u origin nombre-de-la-tarea
```

Después se crea una solicitud de incorporación en GitHub para revisar el cambio
antes de unirlo a `main`. Cada compañero debe conservar su propio `.env` y su
propia `.venv`; ambos están excluidos por `.gitignore`. Nunca se deben subir
contraseñas, archivos temporales ni la carpeta de datos interna de XAMPP.
