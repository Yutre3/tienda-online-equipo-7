# Tienda en línea – Equipo 7

**Integrantes:** Luis Huenchul, Manuel Huichapan y Bastian Lara.

Aplicación de consola desarrollada en Python para administrar clientes, productos, inventario y pedidos. El proyecto adapta al tema de tienda en línea la separación modular del repositorio del profesor `baileytorch/IEI_N2_C2_POO` y demuestra programación orientada a objetos, ORM y conexión segura a MySQL/MariaDB.

Esta versión continúa el trabajo de la Evaluación 2 y agrega la estructura, los repositorios funcionales y el inicio de sesión obligatorio solicitados para la Evaluación 3. No reemplaza el CRUD ni las reglas de inventario anteriores.

## Funciones terminadas

- Clientes: registrar, listar, editar y eliminar.
- Productos: registrar, listar, editar y eliminar con SKU único, precio y stock.
- Pedidos: crear, consultar detalle, agregar o quitar productos, confirmar, cancelar y eliminar.
- Usuarios: registrar, listar, actualizar y deshabilitar con RUT chileno validado y contraseña protegida con bcrypt.
- Acceso: la aplicación solicita correo y contraseña antes de mostrar cualquier operación del menú.
- Inventario transaccional: agregar descuenta stock; quitar, cancelar o eliminar devuelve las unidades correspondientes.
- Validación de nombres, correos, SKU, precios, cantidades, estados e identificadores.
- Tablas de consola con PrettyTable y mensajes comprensibles ante entradas incorrectas.
- Persistencia portátil mediante Peewee y SQLite, lista para usar sin servidor.
- Compatibilidad completa con MySQL/MariaDB mediante PyMySQL.
- Suite automática aislada con SQLite temporal, sin alterar la base real.

## Arquitectura

```text
tienda-online-equipo-7/
├── main.py                   Punto de entrada oficial
├── app.py                    Inicialización compatible y conexión
├── auxiliares/               Nombre y opciones compartidas
├── datos/
│   ├── conexion.py           Inicialización de Peewee
│   ├── model_base.py         ModelBase compartido por todos los modelos
│   ├── configuracion.py      Lectura segura de .env
│   ├── modelos/              Clases ORM
│   ├── repositorio/          Funciones CRUD canónicas
│   ├── repositorios/         Adaptadores para compatibilidad anterior
│   └── sql/                  Esquema, usuario y datos de ejemplo
├── negocio/
│   ├── entidades.py          Clases POO y validaciones
│   └── servicios.py          Reglas y transacciones
├── presentacion/             Menús, entradas y tablas
├── tests/                    Pruebas automáticas
├── DIAGRAMA_UML.md           Diagrama UML en la raíz, según INACAP
├── docs/DIAGRAMA_UML.md      Copia del modelo y las relaciones
├── .env.example              Plantilla sin secretos
├── requirements.txt         Dependencias fijadas
└── .vscode/                  Ejecución, pruebas y SQLTools
```

La presentación no contiene consultas SQL. La capa de negocio no conoce detalles de la consola. Las funciones de `datos/repositorio/` convierten entre objetos del dominio y modelos Peewee; las clases de `datos/repositorios/` delegan en ellas para no romper las importaciones anteriores. Todos los modelos heredan de `datos/model_base.py:ModelBase`, que usa la conexión compartida.

## Dependencias e instalación

- Python 3.12 o superior.
- Visual Studio Code con las extensiones recomendadas.
- MySQL 8 o MariaDB 10.4 es opcional; XAMPP es válido.
- Git para clonar y compartir el proyecto.

Las dependencias directas están fijadas en `requirements.txt`: Peewee, PyMySQL, python-decouple, PrettyTable, bcrypt, maskpass y pytest. No es necesario instalarlas una por una; los pasos siguientes usan el archivo completo.

## Preparación automática en Visual Studio Code

1. Abra la carpeta `TI3021_U2_EF01` mediante **Archivo > Abrir carpeta**.
2. Abra **Terminal > Ejecutar tarea**.
3. Seleccione **Preparar proyecto**.
4. Ejecute la tarea **Ejecutar tienda**. La base SQLite se crea automáticamente con datos de demostración.

La tarea crea `.venv`, instala las dependencias y copia `.env.example` únicamente cuando `.env` todavía no existe. El modo predeterminado es SQLite y no necesita contraseña ni XAMPP. Las contraseñas locales nunca se publican porque `.env` está ignorado por Git.

## Preparación manual

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

## Verificar la conexión desde Visual Studio Code

Seleccione **Terminal > Ejecutar tarea > Verificar conexión de base de datos**. Esta comprobación utiliza el motor indicado en `.env`, consulta las seis tablas (`paises`, `usuarios`, `clientes`, `productos`, `pedidos` y `detalles_pedido`) y muestra su cantidad de registros sin cambiarlos. Para comprobar la base de phpMyAdmin debe configurar `DB_ENGINE=mysql` y las credenciales reales en el `.env` local (no en GitHub); MySQL/XAMPP debe estar iniciado. Para la base SQLite portátil use `DB_ENGINE=sqlite` y ejecute primero **Ejecutar tienda** para crear las tablas si aún no existen.

## Configuración SQLite y creación de la base de datos

La configuración predeterminada usa SQLite. Al ejecutar `main.py`, Peewee crea de forma segura `datos/tienda_online.db` y las seis tablas ausentes: `paises`, `usuarios`, `clientes`, `productos`, `pedidos` y `detalles_pedido`. Se usa `safe=True`; el inicio no ejecuta `DROP TABLE`, no reinicia la base y no borra registros. También se cargan de forma idempotente Chile y los datos de demostración de clientes/productos. Cada compañero obtiene su propia copia editable y persistente, sin depender de que el computador de otro integrante permanezca encendido.

En Visual Studio Code se puede explorar mediante **SQLTools > Tienda Online (SQLite portátil)**. Esta modalidad evita el problema de compartir una dirección `localhost`, ya que `localhost` siempre apunta al computador de quien ejecuta el proyecto.

## Usar MySQL/XAMPP de forma opcional

Inicie MySQL desde XAMPP, MySQL Workbench o el servicio de su sistema. Entre como administrador y ejecute en este orden:

1. `datos/sql/2026.10.05_20.00_DDL_Tienda_Online.sql`
2. Cambie la clave de ejemplo en `datos/sql/2026.10.20_20.10_CREATE_USER.sql` y ejecútelo.
3. Escriba exactamente la misma clave en `DB_PASSWORD` dentro de `.env`.
4. Opcionalmente ejecute `datos/sql/2026.10.20_20.20_DATOS_EJEMPLO.sql`.

La aplicación usa `tienda_app`, una cuenta limitada a la base `tienda_online`. No se utiliza `root` desde Python. Peewee crea las tablas ausentes al iniciar, pero la base y el usuario deben existir previamente.

Si ya utilizaba una versión anterior que tenía productos pero no la columna `sku`, haga primero un respaldo. Al iniciar esta versión, la aplicación asigna códigos `LEGACY-000001`, `LEGACY-000002`, etc. y conserva los registros. También puede ejecutar manualmente `datos/sql/2026.10.20_20.00_MIGRATE_SKU.sql` antes del script de usuario.

Configuración local:

```dotenv
DB_ENGINE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tienda_online
DB_USER=tienda_app
DB_PASSWORD=SU_CLAVE_LOCAL
```

Esta configuración es opcional. No copie una contraseña real al README, a `.env.example` ni a Git; `.env` permanece ignorado. La compatibilidad MySQL debe verificarse en cada equipo con credenciales locales autorizadas.

## Preparación del primer usuario

En una instalación nueva, la aplicación detecta que la tabla `usuarios` está vacía y solicita RUT, nombre, apellido, correo, país, fecha de nacimiento, género y una contraseña oculta mediante maskpass. La clave no tiene un valor predeterminado: se valida y se guarda solo como hash bcrypt.

Este procedimiento aparece exclusivamente cuando no existe ningún usuario. Si una instalación antigua ya contiene cuentas pero ninguna tiene una contraseña bcrypt válida, no se crea una cuenta alternativa. Use de manera local y explícita:

```bash
python -m auxiliares.recuperar_acceso
```

La recuperación exige el correo de una cuenta existente, solicita una nueva clave oculta y cambia solo su hash. No crea usuarios y no habilita cuentas deshabilitadas.

## Inicio de sesión obligatorio

El flujo oficial es **Aplicación → Login → Validación → Menú principal**. El login solicita correo, oculta la contraseña con maskpass, busca mediante Peewee y valida con `bcrypt.checkpw()`. Una cuenta inexistente, deshabilitada, con hash inválido o con clave incorrecta no puede abrir el menú. La persona puede reintentar o salir. La opción `0` del menú cierra la sesión y regresa al formulario de acceso.

## Ejecutar

Desde una terminal con el entorno activado:

```bash
python main.py
```

También puede seleccionar **Ejecutar tienda** en las tareas de Visual Studio Code o la configuración **Ejecutar tienda en línea** en **Ejecutar y depurar**. Al conectarse se muestra `Conexión exitosa. Base de datos preparada.` y aparece primero el login. `python app.py` se conserva como entrada compatible y ejecuta el mismo flujo, sin duplicar inicialización.

El orden recomendado para una demostración es:

1. Registrar un cliente.
2. Registrar dos productos con stock.
3. Crear un pedido para el cliente.
4. Agregar productos y comprobar el total.
5. Confirmar el pedido.
6. Mostrar el resumen general.

## Ejecutar pruebas

Las pruebas utilizan SQLite en memoria únicamente como sustituto controlado de la base. No necesitan XAMPP ni modifican datos reales.

```bash
python -m pytest -q
```

También está disponible la tarea **Ejecutar pruebas**. La suite cubre validaciones, CRUD, claves únicas, relaciones, cálculo de totales, control de stock, transacciones, estados, cancelación, importaciones, presentación y configuración de entrega.

## Principios POO demostrados

- **Encapsulamiento:** nombre, correo, SKU, precio y stock se modifican mediante propiedades validadas.
- **Herencia:** las cuatro entidades heredan identificación común desde `Entidad`; los modelos ORM heredan de `ModeloBase`.
- **Abstracción:** el menú usa `TiendaServicio` sin construir consultas.
- **Asociación y composición:** un cliente realiza pedidos y un pedido compone sus detalles.
- **Reutilización:** repositorios y lectores comunes evitan repetir lógica.
- **Polimorfismo:** todos los modelos Peewee comparten el comportamiento definido por `Model` y `ModeloBase`.

El diagrama completo se encuentra en `DIAGRAMA_UML.md` (raíz) y `docs/DIAGRAMA_UML.md` y puede visualizarse directamente en GitHub o con una extensión Mermaid de Visual Studio Code.

## Reglas importantes

- El correo del cliente y el SKU del producto deben ser únicos.
- El RUT y el correo de cada usuario deben ser únicos; la eliminación de usuarios es lógica para conservar el historial.
- Los precios se guardan como centavos enteros para evitar errores de punto flotante.
- Solo un pedido `CREADO` admite agregar o quitar productos.
- Un pedido vacío no se puede confirmar.
- Un pedido cancelado no puede cambiar nuevamente de estado.
- No se elimina un cliente con pedidos ni un producto referenciado por pedidos conservados.
- Las operaciones de inventario y pedido se ejecutan dentro de una transacción.

## Solución de problemas

Si usa MySQL y aparece **No fue posible conectar con la base de datos**, compruebe que MySQL está iniciado, que la base existe, que `DB_ENGINE=mysql` y que host, puerto, usuario y clave coinciden con `.env`. Para volver al modo que funciona sin servidor, use `DB_ENGINE=sqlite`.

Si PowerShell impide activar el entorno, puede ejecutar directamente:

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe main.py
```

Si un puerto de XAMPP es distinto de 3306, cambie `DB_PORT` en `.env` y el campo `port` de la conexión SQLTools local. No suba esa configuración si incluye credenciales personales.

## Trabajo grupal con Git

Cada integrante debe trabajar en una rama propia:

```bash
git switch main
git pull origin main
git switch -c nombre-de-la-tarea
```

Antes de compartir cambios, ejecute las pruebas y revise que no se incluyan `.env`, `.venv`, archivos ZIP, cachés ni bases locales. Luego cree un commit y una solicitud de incorporación para que otro integrante revise el cambio.

## Entrega

El ZIP o repositorio debe incluir código, pruebas, SQL, documentación y configuración de Visual Studio Code. No debe incluir el entorno virtual, contraseñas ni datos internos de XAMPP. Según la guía de la asignatura, la entrega oficial se carga en AAI; el correo puede utilizarse solo como respaldo o para compartir el trabajo con el equipo.
