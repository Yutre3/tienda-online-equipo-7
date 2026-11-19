# Tienda en línea completa Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar la tienda en línea del Equipo 7 con POO, CRUD, pedidos, ORM Peewee, MySQL, menú, configuración y pruebas.

**Architecture:** El dominio no dependerá de la base de datos; repositorios Peewee traducirán entre entidades y modelos, y los servicios aplicarán reglas transaccionales. La presentación de consola solo leerá datos y llamará a servicios.

**Tech Stack:** Python 3.12+, Peewee, PyMySQL, python-decouple, PrettyTable, pytest, MySQL/MariaDB y SQLite en pruebas.

**Spec:** `docs/superpowers/specs/2026-10-20-tienda-online-final-design.md`

## Global Constraints

- Tema fijo: `Tienda en línea – Equipo 7`.
- MySQL/MariaDB es la base de ejecución y SQLite se usa únicamente en pruebas.
- Precios y totales se representan como centavos enteros.
- Ningún secreto, `.env`, `.venv`, caché ni base local entra al paquete final.
- Solo pedidos `CREADO` admiten cambios de productos.

## Review Focus

- Cantidades mayores al stock deben fallar sin descontar existencias ni alterar totales.
- Cancelar o eliminar un pedido debe devolver stock exactamente una vez.
- Correos y SKU duplicados deben producir un error comprensible.
- Entradas vacías, identificadores inexistentes y valores no numéricos no deben cerrar el menú.
- La configuración de producción no debe usar `root` ni incluir contraseñas reales.

---

### Task 1: Entidades y validaciones POO

**Files:**
- Create: `negocio/entidades.py`
- Modify: `negocio/__init__.py`
- Test: `tests/test_entidades.py`

**Interfaces:**
- Consumes: Ninguna.
- Produces: `Cliente`, `Producto`, `Pedido`, `DetallePedido`, `EstadoPedido` y `ErrorDominio`.

- [ ] **Step 1: Write the failing tests** para normalización de correo/SKU, precio/stock/cantidad inválidos, totales y bloqueo de pedidos no creados.
- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_entidades.py -q`
Expected: FAIL por módulo o símbolos ausentes.

- [ ] **Step 3: Implement the domain classes** con propiedades validadas y asociaciones explícitas.
- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_entidades.py -q`
Expected: PASS.

- [ ] **Step 5: Commit** `feat: modelar dominio de tienda en línea`

### Task 2: Modelos y repositorios Peewee

**Files:**
- Create: `datos/configuracion.py`
- Create: `datos/conexion.py`
- Create: `datos/modelos/__init__.py`
- Create: `datos/modelos/models.py`
- Create: `datos/repositorios/__init__.py`
- Create: `datos/repositorios/tienda.py`
- Replace: `datos/models.py`
- Test: `tests/conftest.py`
- Test: `tests/test_repositorios.py`

**Interfaces:**
- Consumes: Entidades de Task 1.
- Produces: `configurar_base_datos()`, `crear_tablas()`, `RepositorioClientes`, `RepositorioProductos` y `RepositorioPedidos`.

- [ ] **Step 1: Write failing integration tests** para CRUD, relaciones y conversiones usando SQLite temporal real.
- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_repositorios.py -q`
Expected: FAIL por módulos ausentes.

- [ ] **Step 3: Implement Peewee models and repositories** con errores de dominio traducidos y consultas sin SQL manual en la aplicación.
- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_repositorios.py -q`
Expected: PASS.

- [ ] **Step 5: Commit** `feat: agregar persistencia peewee para la tienda`

### Task 3: Servicios transaccionales de la tienda

**Files:**
- Create: `negocio/servicios.py`
- Modify: `negocio/__init__.py`
- Test: `tests/test_servicios.py`

**Interfaces:**
- Consumes: Entidades y repositorios de Tasks 1 y 2.
- Produces: `TiendaServicio` con CRUD y operaciones `crear_pedido`, `agregar_producto`, `quitar_producto`, `confirmar_pedido`, `cancelar_pedido` y `eliminar_pedido`.

- [ ] **Step 1: Write failing service tests** para stock, totales, estados, inexistentes y devolución única de existencias.
- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_servicios.py -q`
Expected: FAIL por servicio ausente.

- [ ] **Step 3: Implement service operations** dentro de transacciones `database.atomic()`.
- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_servicios.py -q`
Expected: PASS.

- [ ] **Step 5: Commit** `feat: completar reglas y pedidos de la tienda`

### Task 4: Presentación y aplicación ejecutable

**Files:**
- Replace: `presentacion/menu.py`
- Create: `presentacion/entradas.py`
- Create: `presentacion/tablas.py`
- Modify: `auxiliares/info_app.py`
- Modify: `auxiliares/opciones_menu.py`
- Replace: `app.py`
- Test: `tests/test_presentacion.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `TiendaServicio` de Task 3.
- Produces: menú principal y submenús resilientes, `crear_servicio()` y `main()`.

- [ ] **Step 1: Write failing presentation tests** para parseo, formato, navegación y error de conexión controlado.
- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_presentacion.py tests/test_app.py -q`
Expected: FAIL por interfaz ausente.

- [ ] **Step 3: Implement menus, tables and entrypoint** sin lógica SQL en presentación.
- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_presentacion.py tests/test_app.py -q`
Expected: PASS.

- [ ] **Step 5: Commit** `feat: completar menú de administración de tienda`

### Task 5: Entorno, SQL y documentación de entrega

**Files:**
- Replace: `requirements.txt`
- Replace: `.env.example`
- Modify: `.gitignore`
- Modify: `.vscode/extensions.json`
- Modify: `.vscode/launch.json`
- Modify: `.vscode/settings.json`
- Modify: `.vscode/tasks.json`
- Replace: `datos/sql/2026.10.05_20.00_DDL_Tienda_Online.sql`
- Create: `datos/sql/2026.10.20_20.10_CREATE_USER.sql`
- Create: `datos/sql/2026.10.20_20.20_DATOS_EJEMPLO.sql`
- Replace: `README.md`
- Create: `docs/DIAGRAMA_UML.md`
- Test: `tests/test_configuracion_entrega.py`

**Interfaces:**
- Consumes: La aplicación completa.
- Produces: instalación reproducible, usuario limitado, esquema, datos de muestra, tareas de VS Code y guía de uso.

- [ ] **Step 1: Write failing delivery tests** para requisitos, configuración segura, scripts y archivos excluidos.
- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_configuracion_entrega.py -q`
Expected: FAIL por contenido incompleto.

- [ ] **Step 3: Implement delivery assets** y documentar instalación, ejecución, CRUD, estructura y UML.
- [ ] **Step 4: Run full verification**

Run: `python -m pytest -q && python -m compileall -q app.py auxiliares datos negocio presentacion`
Expected: PASS y código de salida 0.

- [ ] **Step 5: Commit** `docs: finalizar entorno y entrega de tienda`
