# Instrucciones completas para XAMPP y la base de datos

La solución utiliza MariaDB de XAMPP, phpMyAdmin, Python y el conector oficial
MySQL Connector/Python. La base se llama `tienda_online`.

## 1. Programas necesarios

- XAMPP 8.2.12 para Linux, que incluye Apache, MariaDB y phpMyAdmin.
- Python 3.10 o superior.
- MySQL Connector/Python 26.7.0.

Python ya está instalado en este equipo. El instalador oficial de XAMPP ya se
descargó y validó en:

```text
/tmp/xampp-linux-x64-8.2.12-0-installer.run
```

## 2. Instalar XAMPP

La instalación necesita la contraseña administrativa del equipo. Ejecute en
una terminal propia:

```bash
sudo /tmp/xampp-linux-x64-8.2.12-0-installer.run --mode unattended
```

XAMPP quedará instalado en `/opt/lampp`.

Comprobar la instalación:

```bash
/opt/lampp/lampp version
```

## 3. Entrar a la carpeta del proyecto

```bash
cd /home/diego/Proyectos/xxxxxxx/TI3021_U2_EF01
```

## 4. Instalar el conector oficial de Python

Crear el entorno virtual:

```bash
python3 -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

Instalar el conector:

```bash
python -m pip install -r requirements.txt
```

Cuando vuelva a abrir una terminal deberá entrar a la carpeta y ejecutar otra
vez `source .venv/bin/activate` antes de utilizar los programas Python.

## 5. Iniciar XAMPP

```bash
sudo /opt/lampp/lampp start
```

El resultado debe indicar que Apache y MySQL están iniciados.

Comprobar el estado:

```bash
sudo /opt/lampp/lampp status
```

## 6. Crear la base automáticamente

Con el entorno virtual activo y XAMPP iniciado:

```bash
python crear_base_datos.py
```

El programa crea la base `tienda_online` y sus tablas. Puede ejecutarse más de
una vez sin borrar los datos existentes.

Las tablas creadas son:

- `clientes`
- `productos`
- `pedidos`
- `detalles_pedido`

Todas utilizan InnoDB. Las relaciones se protegen con tres claves foráneas.

## 7. Crear la base desde phpMyAdmin

Esta es una alternativa al comando Python:

1. Inicie XAMPP.
2. Abra `http://localhost/phpmyadmin` en el navegador.
3. Entre en la pestaña **Importar**.
4. Seleccione el archivo `schema.sql` de esta carpeta.
5. Pulse **Importar** o **Continuar**.
6. Compruebe que aparezca la base `tienda_online` en el panel izquierdo.

El archivo que se debe importar es:

```text
/home/diego/Proyectos/xxxxxxx/TI3021_U2_EF01/schema.sql
```

## 8. Probar la conexión

```bash
python probar_conexion.py
```

Resultado esperado:

```text
Conexión exitosa con 'tienda_online' en 127.0.0.1:3306.
```

## 9. Verificar toda la base

```bash
python verificar_sistema.py
```

El programa comprueba:

1. Que MariaDB de XAMPP esté iniciado.
2. Que Python pueda conectarse.
3. Que existan las cuatro tablas.
4. Que todas las tablas usen InnoDB.
5. Que estén activas las tres claves foráneas.

El último mensaje debe ser:

```text
Sistema XAMPP verificado y operativo.
```

## 10. Usar el programa de administración

```bash
python administrar_tienda.py
```

El menú permite:

1. Registrar clientes.
2. Registrar productos con precio y stock.
3. Crear pedidos.
4. Agregar productos a pedidos.
5. Consultar clientes, productos y pedidos.

El programa descuenta el stock y calcula el total del pedido dentro de una
transacción. Si ocurre un error, MariaDB revierte todos los cambios de esa
operación.

## 11. Entrar a la base por consola

```bash
/opt/lampp/bin/mysql -u root
```

Dentro de MariaDB:

```sql
USE tienda_online;
SHOW TABLES;
DESCRIBE clientes;
DESCRIBE productos;
DESCRIBE pedidos;
DESCRIBE detalles_pedido;
SELECT * FROM clientes;
SELECT * FROM productos;
SELECT * FROM pedidos;
SELECT * FROM detalles_pedido;
EXIT;
```

## 12. Configuración de conexión

La configuración predeterminada de XAMPP es:

```text
Servidor: 127.0.0.1
Puerto: 3306
Base: tienda_online
Usuario: root
Contraseña: vacía
```

Si se configura una contraseña o un usuario diferente, defina las variables
antes de ejecutar Python:

```bash
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_NAME=tienda_online
export DB_USER=root
export DB_PASSWORD='CONTRASEÑA_CONFIGURADA_EN_XAMPP'
```

No escriba una contraseña real dentro del código ni la publique en GitHub.

## 13. Ejecutar las pruebas

```bash
python -m unittest -v
```

Las pruebas crean registros identificables, comprueban persistencia, stock y
totales, y eliminan únicamente sus propios registros al finalizar.

## 14. Detener XAMPP

Cuando termine:

```bash
sudo /opt/lampp/lampp stop
```

## 15. Evidencias para la evaluación

Guarde capturas de:

1. XAMPP con Apache y MySQL iniciados.
2. phpMyAdmin mostrando `tienda_online` y sus cuatro tablas.
3. Las relaciones de las tablas en phpMyAdmin.
4. El diagrama `diagrama_uml.puml` abierto en un visor PlantUML.
5. El resultado de `python probar_conexion.py`.
6. El resultado de `python verificar_sistema.py`.
7. El resultado de `python -m unittest -v`.

## 16. Solución de problemas

Si aparece `Access denied`, el usuario o la contraseña no coinciden con la
configuración de MariaDB. Configure `DB_USER` y `DB_PASSWORD` como se explica
en la sección 12.

Si aparece `Can't connect to MySQL server`, MariaDB no está iniciado. Ejecute:

```bash
sudo /opt/lampp/lampp start
```

Si Apache no inicia porque el puerto 80 está ocupado, MariaDB todavía puede
usarse desde Python y desde `/opt/lampp/bin/mysql`. Para utilizar phpMyAdmin se
debe liberar o cambiar el puerto de Apache.

Si Python indica que no existe el módulo `mysql`, active `.venv` e instale las
dependencias de la sección 4.
