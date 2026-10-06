# Tienda en línea - Equipo 7

Proyecto modular de Programación Orientada a Objetos en Python. Está organizado
siguiendo la estructura utilizada por el profesor, pero todo el contenido
corresponde al tema de la tienda en línea: clientes, productos, stock, pedidos y
detalles de pedido.

## Estructura

```text
TI3021_U2_EF01/
├── auxiliares/
│   ├── __init__.py
│   ├── info_app.py
│   └── opciones_menu.py
├── datos/
│   ├── sql/
│   │   └── 2026.10.05_20.00_DDL_Tienda_Online.sql
│   ├── __init__.py
│   └── models.py
├── negocio/
│   └── __init__.py
├── presentacion/
│   ├── __init__.py
│   └── menu.py
├── app.py
├── .gitignore
└── README.md
```

- `datos/models.py`: clases POO, conexión y persistencia en MariaDB.
- `datos/sql`: definición versionada de la base de datos.
- `negocio`: operaciones de la tienda.
- `presentacion/menu.py`: menú de consola.
- `auxiliares`: nombre y opciones de la aplicación.
- `app.py`: punto de entrada.

## Programas necesarios

- Python 3.10 o superior.
- Visual Studio Code con la extensión oficial de Python.
- XAMPP con MySQL/MariaDB iniciado.
- Git.

## Abrir como el proyecto del profesor

1. Abra Visual Studio Code.
2. Seleccione **Archivo > Abrir carpeta**.
3. Abra la carpeta `TI3021_U2_EF01`.
4. El explorador mostrará `datos`, `negocio`, `presentacion`, `auxiliares`,
   `app.py`, `.env`, `.gitignore` y `README.md`.

## Preparar el proyecto

En Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install mysql-connector-python==26.7.0
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install mysql-connector-python==26.7.0
```

## Configurar la conexión

Cree un archivo `.env` en la raíz con estos valores:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tienda_online
DB_USER=root
DB_PASSWORD=
```

Si otro computador usa credenciales diferentes, solo debe cambiar `DB_USER` y
`DB_PASSWORD`. El archivo `.env` no se publica en GitHub.

## Base de datos

El esquema está incluido en
`datos/sql/2026.10.05_20.00_DDL_Tienda_Online.sql`. La aplicación crea la base y
las tablas automáticamente al iniciarse. También puede importarse ese archivo
desde phpMyAdmin.

Tablas:

- `clientes`
- `productos`
- `pedidos`
- `detalles_pedido`

## Ejecutar

Inicie MySQL desde XAMPP y ejecute:

```bash
python app.py
```

El menú permite registrar clientes, registrar productos, crear pedidos, agregar
productos y consultar los datos almacenados.

## Git y GitHub

Después de clonar:

```bash
git clone https://github.com/Yutre3/tienda-online-equipo-7.git
cd tienda-online-equipo-7
```

Para trabajar en equipo:

```bash
git pull
git switch -c nombre-de-la-tarea
git add archivo_modificado.py
git commit -m "Descripción del cambio"
git push -u origin nombre-de-la-tarea
```

No publique `.env`, `.venv`, contraseñas, archivos temporales ni bases locales.

## Referencia

La organización se adaptó desde
[IEC_N2_C1_POO](https://github.com/baileytorch/IEC_N2_C1_POO), sin copiar su tema
de biblioteca ni sus datos.
