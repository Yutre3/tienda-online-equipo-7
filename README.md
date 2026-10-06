# Tienda en línea — Equipo 7

Proyecto de la asignatura TI3021, desarrollado en Python con programación
orientada a objetos y persistencia real en MariaDB/MySQL. El sistema administra
clientes, productos, existencias, pedidos y detalles de pedido. Al agregar un
producto a un pedido descuenta el stock y actualiza el total en una sola
transacción.

La organización toma como referencia la separación modular mostrada por el
profesor, pero todo el dominio, las clases y la base corresponden a la tienda en
línea del Equipo 7.

## Estructura del proyecto

```text
TI3021_U2_EF01/
├── app.py                         # punto de entrada
├── auxiliares/                    # constantes reutilizables
│   └── opciones_menu.py           # opciones del menú de la tienda
├── datos/
│   ├── configuracion.py           # carga de .env y validación
│   ├── conexion.py                # conexión y transacciones
│   ├── models.py                  # conversión de registros a modelos POO
│   ├── repositorios.py            # consultas SQL
│   └── sql/001_esquema.sql        # base de datos versionada
├── negocio/
│   ├── entidades.py               # Cliente, Producto, Pedido y DetallePedido
│   └── servicios.py               # casos de uso y reglas de la tienda
├── presentacion/menu.py           # interfaz por consola
├── scripts/                       # creación y verificación de la base
├── tests/                         # pruebas unitarias y de integración
├── diagrama_uml.puml              # modelo UML del proyecto
├── .env.example                   # plantilla de conexión sin secretos
├── requirements.txt               # dependencias declaradas
└── TI3021_U2_EF01.code-workspace  # espacio de trabajo de VS Code
```

El código depende de las capas en este orden:

```text
presentación → negocio → repositorio → conexión → MariaDB
```

## Programas necesarios

- Python 3.10 o superior.
- Visual Studio Code, que es el programa mostrado en la captura de referencia.
- Extensión oficial **Python** de Microsoft para Visual Studio Code.
- XAMPP con MariaDB/MySQL iniciado, o un servidor MySQL/MariaDB equivalente.
- Git para el trabajo grupal.

No se debe subir `.venv`, `.env`, contraseñas, archivos `__pycache__` ni una base
local temporal. La estructura oficial de la base está incluida en
`datos/sql/001_esquema.sql` y se reconstruye sin rutas del computador original.

## Preparación después de clonar

Abra una terminal dentro de la carpeta clonada y entre al proyecto:

```bash
cd TI3021_U2_EF01
```

En Windows PowerShell:

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

Cada integrante crea su propio `.venv` y `.env`; esos archivos locales no se
comparten por Git.

## Abrir en Visual Studio Code

1. Inicie Visual Studio Code.
2. Seleccione **Archivo > Abrir área de trabajo desde archivo**.
3. Abra `TI3021_U2_EF01.code-workspace`.
4. Acepte la instalación de las extensiones recomendadas.
5. Si se solicita un intérprete, elija el Python de `.venv`.
6. El explorador mostrará `datos`, `negocio`, `presentacion`, `scripts` y
   `tests`, de forma semejante a la organización del profesor.

También puede abrir la carpeta directamente. La configuración de `.vscode`
incluye ejecución, depuración, pruebas y una conexión orientativa para SQLTools.
La aplicación obtiene sus datos únicamente desde `.env`. Si usa SQLTools y sus
credenciales son diferentes, edite la conexión desde la interfaz de la extensión;
no guarde una contraseña real en `.vscode/settings.json` porque ese archivo sí se
comparte por Git.

## Configurar la base de datos

Inicie **MySQL/MariaDB** desde el panel de XAMPP. Después revise `.env`:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tienda_online
DB_USER=root
DB_PASSWORD=
```

Estos son los únicos valores que normalmente cambian entre computadores. Si el
usuario de MariaDB tiene contraseña, escríbala solo en el `.env` local. Nunca la
suba a GitHub.

Con XAMPP iniciado, cree la base y sus cuatro tablas:

```bash
python -m scripts.crear_base_datos
```

El comando lee `datos/sql/001_esquema.sql`; puede repetirse sin borrar los datos
existentes. Como alternativa, importe ese archivo desde la pestaña **Importar**
de phpMyAdmin. Las tablas incluidas son:

- `clientes`
- `productos`
- `pedidos`
- `detalles_pedido`

Todas usan InnoDB, restricciones y claves foráneas. El repositorio contiene el
esquema reproducible, no una copia dependiente de una instalación particular de
XAMPP. Si cambia `DB_NAME`, use el comando automático: la importación manual del
archivo SQL utiliza el nombre predeterminado `tienda_online`.

## Comprobar y ejecutar

Pruebe solo la conexión:

```bash
python -m scripts.probar_conexion
```

Verifique la conexión y todas las tablas:

```bash
python -m scripts.verificar_sistema
```

Ejecute la aplicación:

```bash
python app.py
```

También puede pulsar `F5` en Visual Studio Code y elegir **Ejecutar tienda en
línea**. El menú permite registrar clientes y productos, crear pedidos, agregar
productos y consultar los datos guardados.

## Ejecutar las pruebas

```bash
python -m unittest discover -s tests -v
```

Las pruebas de las entidades funcionan sin servidor. La prueba de integración
usa la base configurada y se omite con un mensaje claro cuando MariaDB no está
disponible.

## Cómo modificar el proyecto

- Cambios de tablas o relaciones: `datos/sql/001_esquema.sql`.
- Cambios de conexión: `.env` local y `datos/configuracion.py`.
- Consultas a la base: `datos/repositorios.py`.
- Clases y validaciones POO: `negocio/entidades.py`.
- Casos de uso: `negocio/servicios.py`.
- Textos y opciones de consola: `presentacion/menu.py`.
- Punto de inicio: `app.py`.

Mantenga esta separación: la presentación no debe escribir SQL y las entidades
no deben leer variables del computador.

## Trabajo grupal con Git y GitHub

Antes de comenzar una tarea:

```bash
git switch main
git pull
git switch -c nombre-corto-de-la-tarea
```

Después de modificar y probar:

```bash
git status
git add ruta/del/archivo_modificado.py
git commit -m "Descripción breve del cambio"
git push -u origin nombre-corto-de-la-tarea
```

Luego se crea una solicitud de incorporación (*pull request*) en GitHub para que
otro integrante revise el cambio antes de unirlo a `main`. No use `git add .`
sin revisar `git status`, y no suba `.env` ni contraseñas.

## Problemas frecuentes

- **No fue posible conectar con MariaDB:** inicie MySQL en XAMPP y revise host,
  puerto, usuario y contraseña en `.env`.
- **Access denied:** MariaDB rechazó el usuario o la contraseña configurados.
- **Unknown database:** ejecute `python -m scripts.crear_base_datos`.
- **No module named mysql:** active `.venv` e instale `requirements.txt`.
- **PowerShell bloquea Activate.ps1:** puede ejecutar los comandos con
  `.venv\Scripts\python.exe` sin activar el entorno.

## Referencia de organización

La separación modular se adaptó desde el repositorio docente
[IEC_N2_C1_POO](https://github.com/baileytorch/IEC_N2_C1_POO). No se copiaron su
tema de biblioteca ni sus datos.
