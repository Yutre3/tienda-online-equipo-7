# Diseño final de Tienda en línea – Equipo 7

## Propósito

Entregar un proyecto académico ejecutable que adapte la arquitectura del repositorio `baileytorch/IEI_N2_C2_POO` al tema del Equipo 7: una tienda en línea. Debe demostrar programación orientada a objetos, modularización, conexión segura a MySQL/MariaDB y operaciones persistentes desde un menú de consola.

## Objetivos

- Mantener capas equivalentes a las del profesor: `auxiliares`, `presentacion`, `negocio` y `datos`.
- Usar Peewee como ORM, PyMySQL como controlador, `python-decouple` para `.env` y PrettyTable para mostrar registros.
- Representar clientes, productos, pedidos y detalles mediante clases relacionadas y encapsuladas.
- Permitir crear, consultar, actualizar y eliminar clientes y productos respetando relaciones.
- Permitir crear pedidos, agregar y quitar productos, confirmar o cancelar pedidos y consultar sus detalles.
- Controlar stock y totales dentro de transacciones; cancelar o eliminar un pedido devuelve sus existencias.
- Entregar scripts SQL reproducibles, configuración portable de Visual Studio Code y documentación suficiente para otro integrante.
- Probar las reglas y repositorios sin depender de un servidor externo, usando una base SQLite temporal únicamente en pruebas.

## Límites

- Es una aplicación de consola; no se creará interfaz web ni gráfica.
- No incluye pagos, despacho, autenticación de clientes ni servicios externos.
- MySQL/MariaDB es la base de ejecución. SQLite solo facilita pruebas automáticas aisladas.
- No se incluyen secretos ni la carpeta `.venv` en el paquete final.

## Arquitectura

- `negocio/entidades.py`: objetos de dominio, enumeración de estados y validaciones.
- `datos/conexion.py`: configuración y conexión Peewee obtenida desde `.env`.
- `datos/modelos/`: modelos ORM y relaciones.
- `datos/repositorios/`: CRUD y consultas persistentes.
- `negocio/servicios.py`: coordinación transaccional y reglas de pedidos/stock.
- `presentacion/`: lectura validada, submenús y tablas.
- `auxiliares/`: metadatos y opciones compartidas.
- `datos/sql/`: creación de base, usuario, esquema y datos de ejemplo.

## Decisiones asumidas

- El precio se almacena como centavos enteros para evitar errores de punto flotante.
- Un correo identifica de manera única a cada cliente y el código SKU identifica a cada producto.
- Solo los pedidos en estado `CREADO` se pueden modificar.
- Confirmar conserva el stock ya descontado; cancelar o eliminar devuelve el stock.
- No se puede eliminar un cliente con pedidos ni un producto presente en pedidos conservados.
- La conexión predeterminada usa el usuario limitado `tienda_app`, no `root`.

## Criterio de finalización

El proyecto queda finalizado cuando la suite automática pasa, todos los módulos compilan, los scripts y configuraciones no contienen secretos, el menú expone los flujos definidos y el ZIP final contiene únicamente archivos necesarios para clonar, instalar y ejecutar el sistema.
