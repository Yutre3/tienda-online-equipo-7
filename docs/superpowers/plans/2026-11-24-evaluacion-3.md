# Evaluación 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar la estructura, persistencia funcional, seguridad y flujo de ejecución exigidos por los once criterios de la Evaluación 3 sin reemplazar el CRUD ni las reglas de inventario existentes.

**Architecture:** Los modelos compartirán un único `ModelBase`; `datos/repositorio/` será la capa funcional canónica y las clases históricas delegarán en ella. `app.py` conservará la inicialización y coordinará un bucle finito de autenticación antes del menú; `main.py` será un envoltorio mínimo.

**Tech Stack:** Python 3.12+, Peewee, SQLite/MySQL, bcrypt, maskpass, pytest, Git.

**Spec:** `docs/superpowers/specs/2026-11-24-evaluacion-3-design.md`

## Global Constraints

- Trabajar en el repositorio existente `Yutre3/tienda-online-equipo-7`; no crear otro proyecto ni eliminar funciones de la Evaluación 2.
- No usar `DROP TABLE`, reiniciar bases, borrar datos, publicar credenciales, `git reset --hard`, `git push --force` ni operaciones destructivas.
- Conservar las seis tablas: `paises`, `usuarios`, `clientes`, `productos`, `pedidos`, `detalles_pedido`.
- Conservar SQLite y MySQL/MariaDB; MySQL solo se declara verificado con credenciales locales autorizadas y una consulta real.
- Conservar reglas de pedidos, estados, totales, transacciones y stock; el descuento condicional sigue siendo SQL atómico.
- Toda función o cambio de comportamiento nuevo sigue RED-GREEN antes del código de producción.

## Review Focus

- Base con usuarios existentes pero hashes inválidos: no debe ofrecer un alta que eluda la autenticación; Task 3 lo prueba.
- Base con todas las cuentas deshabilitadas: debe distinguir el bloqueo y no reactivarlas; Task 3 lo prueba.
- Deshabilitar la última cuenta durante una sesión y cerrar sesión: debe reevaluar el estado antes de otro login; Task 3 lo prueba.
- Base vacía sin país habilitado: debe terminar con explicación, no ciclar en el formulario; Task 3 lo prueba.
- Concurrencia al descontar stock: debe conservar la actualización condicional que evita stock negativo; Task 2 reutiliza y ejecuta las pruebas concurrentes existentes.

---

### Task 1: ModelBase único y estructura ORM obligatoria

**Files:**
- Create: `datos/model_base.py`
- Modify: `datos/modelos/models.py`
- Modify: `datos/modelos/__init__.py`
- Test: `tests/test_arquitectura_evaluacion3.py`

**Interfaces:**
- Consumes: `datos.conexion.base_datos_proxy`.
- Produces: `ModelBase`, alias idéntico `ModeloBase`, y seis modelos cuya clase base directa es `ModelBase`.

- [ ] **Step 1: Write the failing architecture tests**

Crear `test_model_base_es_unico_y_usa_la_conexion_compartida` y `test_todos_los_modelos_heredan_de_model_base`. Deben importar `ModelBase` y `ModeloBase`, comprobar identidad, subclase de `peewee.Model`, base compartida y herencia de las seis clases.

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv/bin/python -m pytest tests/test_arquitectura_evaluacion3.py -q`

Expected: FAIL de colección porque `datos.model_base` no existe.

- [ ] **Step 3: Implement the shared base**

Definir `class ModelBase(Model)` con `Meta.database = base_datos_proxy`, definir `ModeloBase = ModelBase`, eliminar la definición local de `ModeloBase` y hacer que todos los modelos hereden de `ModelBase`. Reexportar ambos nombres sin duplicar configuración.

- [ ] **Step 4: Verify GREEN and regression suite**

Run: `.venv/bin/python -m pytest tests/test_arquitectura_evaluacion3.py -q && .venv/bin/python -m pytest -q`

Expected: pruebas nuevas y suite completa PASS.

- [ ] **Step 5: Commit**

Run: `git add datos/model_base.py datos/modelos/models.py datos/modelos/__init__.py tests/test_arquitectura_evaluacion3.py && git commit -m "refactor: centralizar ModelBase de Peewee"`

---

### Task 2: Repositorios funcionales canónicos y adaptadores compatibles

**Files:**
- Create: `datos/repositorio/__init__.py`
- Create: `datos/repositorio/clientes.py`
- Create: `datos/repositorio/productos.py`
- Create: `datos/repositorio/pedidos.py`
- Create: `datos/repositorio/usuarios.py`
- Create: `datos/repositorio/paises.py`
- Modify: `datos/repositorios/tienda.py`
- Modify: `datos/repositorios/repositorio_usuario.py`
- Modify: `datos/repositorios/repositorio_pais.py`
- Modify: `datos/repositorios/__init__.py`
- Test: `tests/test_repositorios_funcionales.py`
- Test: `tests/test_repositorios.py`
- Test: `tests/test_usuarios.py`
- Test: `tests/test_servicios.py`

**Interfaces:**
- Consumes: modelos ORM de Task 1 y entidades actuales de `negocio.entidades`.
- Produces: funciones `guardar/obtener/listar/modificar/eliminar` por entidad; operaciones auxiliares de stock y detalle; clases `Repositorio*` con contratos públicos sin cambios.

- [ ] **Step 1: Write failing function-repository tests**

Crear pruebas que importen el paquete singular, comprueben con `inspect.isfunction` que las operaciones públicas son funciones y ejerzan con SQLite real: guardar mediante `save()`, listar, buscar, modificar y eliminar/deshabilitar clientes, productos, pedidos, usuarios y países. La mutación que deben detectar es volver a dejar una entidad implementada únicamente mediante una clase.

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv/bin/python -m pytest tests/test_repositorios_funcionales.py -q`

Expected: FAIL de colección porque `datos.repositorio` no existe.

- [ ] **Step 3: Implement canonical functional modules**

Firmas mínimas:

- clientes: `guardar_cliente(Cliente) -> Cliente`, `obtener_cliente(int) -> Cliente`, `listar_clientes() -> list[Cliente]`, `modificar_cliente(Cliente) -> Cliente`, `eliminar_cliente(int) -> None`;
- productos: equivalentes y `descontar_stock(int, int)`, `reponer_stock(int, int)`;
- pedidos: `guardar_pedido(Pedido)`, `obtener_pedido`, `obtener_pedido_para_actualizar`, `listar_pedidos`, `guardar_detalle`, `eliminar_detalle`, `cambiar_estado_pedido`, `eliminar_pedido`, `recalcular_total`;
- usuarios: `guardar_usuario`, tres listados, `obtener_usuario_rut`, `obtener_usuario_correo` y funciones de estado usadas por Task 3;
- países: `listado_paises`, `buscar_paises`, `obtener_pais_id`.

Usar modelos más `save()` para altas/modificaciones. Conservar actualizaciones SQL atómicas de stock y todas las traducciones de `IntegrityError` a `ErrorDominio`.

- [ ] **Step 4: Replace classes with pure delegation**

Mantener los nombres y métodos de `RepositorioClientes`, `RepositorioProductos`, `RepositorioPedidos`, `RepositorioUsuarios` y `RepositorioPaises`, pero cada método solo llama a una función canónica. Reexportar las funciones históricas sin ciclos ni recursión.

- [ ] **Step 5: Verify GREEN, CRUD and inventory regressions**

Run: `.venv/bin/python -m pytest tests/test_repositorios_funcionales.py tests/test_repositorios.py tests/test_usuarios.py tests/test_servicios.py -q && .venv/bin/python -m pytest -q`

Expected: pruebas funcionales, CRUD, migración, pedidos, concurrencia e inventario PASS.

- [ ] **Step 6: Commit**

Run: `git add datos/repositorio datos/repositorios tests/test_repositorios_funcionales.py && git commit -m "refactor: implementar repositorios mediante funciones"`

---

### Task 3: Login obligatorio, alta inicial y recuperación local

**Files:**
- Modify: `app.py`
- Modify: `negocio/servicios.py`
- Modify: `presentacion/menu.py`
- Modify: `presentacion/presentacion_usuario.py`
- Modify: `auxiliares/opciones_menu.py`
- Create: `auxiliares/recuperar_acceso.py`
- Test: `tests/test_flujo_autenticacion.py`
- Modify: `tests/test_presentacion_usuario.py`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `login_usuario()`, `TiendaServicio.autenticar_usuario()`, CRUD de usuarios y funciones de estado de Task 2.
- Produces: `TiendaServicio.estado_acceso_usuarios() -> str`, `TiendaServicio.cambiar_contrasenia_usuario_existente(...)`, `preparar_primer_usuario(...)`, `app.ejecutar_aplicacion(...) -> int`, `auxiliares.recuperar_acceso.main() -> int`.

- [ ] **Step 1: Write failing login-flow tests**

Cubrir por comportamiento: el menú no se invoca antes de autenticar; credenciales correctas abren menú; contraseña incorrecta, usuario inexistente y deshabilitado no lo abren; cancelar permite salir; logout vuelve al login; no existe opción interna para iniciar sesión; tras deshabilitar la última cuenta el siguiente ciclo se bloquea.

- [ ] **Step 2: Write failing bootstrap and recovery tests**

Cubrir: tabla vacía permite crear exactamente el primer usuario con hash bcrypt; tabla con cualquier usuario impide el alta inicial; hash inválido orienta a recuperación sin crear otra cuenta; todas deshabilitadas no se reactivan; sin país termina con explicación; recuperación cambia solo `password` de una cuenta existente y conserva `habilitado` y el resto de campos.

- [ ] **Step 3: Run tests to verify RED**

Run: `.venv/bin/python -m pytest tests/test_flujo_autenticacion.py tests/test_app.py tests/test_presentacion_usuario.py -q`

Expected: FAIL porque faltan `ejecutar_aplicacion`, estado de acceso, alta inicial y recuperación, y porque el menú aún contiene login.

- [ ] **Step 4: Implement account-state and recovery services**

Estados literales: `sin_usuarios`, `disponible`, `sin_password_valido`, `sin_habilitados`. Reutilizar `_preparar_hash_bcrypt` y `crear_hash_contrasenia`. La recuperación debe buscar una cuenta existente, validar la nueva clave, guardar el hash y no tocar `habilitado`.

- [ ] **Step 5: Implement controlled bootstrap and authenticated loop**

Reutilizar `crear_usuario()` para el formulario inicial y `login_usuario()` para credenciales. Capturar `ErrorDominio` en el coordinador, ofrecer reintento/salida con respuestas acotadas, reevaluar cuentas en cada vuelta y manejar `EOFError`/`KeyboardInterrupt` sin traza. Cambiar la opción `0` del menú a cierre de sesión y eliminar la opción de login posterior.

- [ ] **Step 6: Implement explicit local recovery command**

`python -m auxiliares.recuperar_acceso` debe preparar la misma base, solicitar correo y clave oculta, modificar solo una cuenta existente, cerrar la conexión y devolver código distinto de cero ante un error explicado.

- [ ] **Step 7: Verify GREEN and full suite**

Run: `.venv/bin/python -m pytest tests/test_flujo_autenticacion.py tests/test_app.py tests/test_presentacion_usuario.py tests/test_usuarios.py -q && .venv/bin/python -m pytest -q`

Expected: todos los escenarios de login, seguridad, bootstrap, recuperación y regresión PASS.

- [ ] **Step 8: Commit**

Run: `git add app.py negocio/servicios.py presentacion/menu.py presentacion/presentacion_usuario.py auxiliares/opciones_menu.py auxiliares/recuperar_acceso.py tests && git commit -m "feat: exigir autenticacion antes del menu"`

---

### Task 4: Punto de entrada, Visual Studio Code y documentación evaluable

**Files:**
- Create: `main.py`
- Modify: `.vscode/launch.json`
- Modify: `.vscode/tasks.json`
- Modify: `README.md`
- Modify: `tests/test_configuracion_entrega.py`
- Create: `tests/test_puntos_entrada.py`

**Interfaces:**
- Consumes: `app.main() -> int` de Task 3.
- Produces: ejecución oficial `python main.py`, compatibilidad `python app.py`, tareas VS Code y documentación de instalación/operación.

- [ ] **Step 1: Write failing entry-point and configuration tests**

Probar con ejecución real controlada que `main.py` existe, delega en `app.main`, puede arrancar sin traza y `app.py` conserva el mismo flujo. Validar JSON de VS Code y que ejecutar tienda usa `main.py`. Extender las pruebas documentales para exigir integrantes, dependencias, SQLite, creación de base, MySQL opcional, primer usuario, login, recuperación, `python main.py`, pruebas y capas.

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv/bin/python -m pytest tests/test_puntos_entrada.py tests/test_configuracion_entrega.py -q`

Expected: FAIL porque `main.py` no existe y VS Code/README todavía usan `app.py` como recorrido oficial.

- [ ] **Step 3: Implement the minimal official entry point and VS Code changes**

`main.py` importa `main` desde `app` y ejecuta `raise SystemExit(main())`; no duplica conexión ni menús. Cambiar tareas y lanzamiento para ejecutar `main.py`.

- [ ] **Step 4: Rewrite README preserving useful Evaluation 2 content**

Documentar los trece puntos pedidos, la estructura singular obligatoria y la carpeta plural de compatibilidad. No incluir credenciales utilizables ni afirmar verificación MySQL no realizada.

- [ ] **Step 5: Verify GREEN and full suite**

Run: `.venv/bin/python -m pytest tests/test_puntos_entrada.py tests/test_configuracion_entrega.py -q && .venv/bin/python -m pytest -q`

Expected: puntos de entrada, JSON, documentación y suite completa PASS.

- [ ] **Step 6: Commit**

Run: `git add main.py .vscode README.md tests/test_puntos_entrada.py tests/test_configuracion_entrega.py && git commit -m "docs: preparar ejecucion y entrega de evaluacion 3"`

---

### Task 5: Verificación integral, matriz de rúbrica y preparación de publicación

**Files:**
- Create: `docs/EVALUACION_3_VERIFICACION.md`
- Modify only if a failing verification exposes a defect: relevant production/test file using RED-GREEN.

**Interfaces:**
- Consumes: todos los entregables de Tasks 1-4.
- Produces: evidencia reproducible por cada uno de los once criterios y árbol listo para revisión/publicación.

- [ ] **Step 1: Run all automated verification**

Run: `.venv/bin/python -m pytest -q`

Expected: all tests PASS with the exact count recorded.

Run: `.venv/bin/python -m compileall -q app.py main.py auxiliares datos negocio presentacion tests`

Expected: exit 0.

Run: `git diff --check && git grep -nE '^(<<<<<<<|=======|>>>>>>>)' -- . ':!docs/superpowers' || true`

Expected: no whitespace errors and no conflict markers.

- [ ] **Step 2: Verify SQLite and Visual Studio Code without real data**

Usar una ruta SQLite temporal para arrancar, crear las seis tablas, autenticar/cerrar de forma controlada y reabrir para comprobar persistencia. Analizar los cuatro JSON de `.vscode`.

Expected: seis tablas, persistencia comprobada, JSON válido, base real rastreada sin cambios.

- [ ] **Step 3: Attempt authorized MySQL verification conditionally**

Si existe `.env` con `DB_ENGINE=mysql`, ejecutar `verificar_base_datos.py` sin imprimir variables ni secretos. Si no existe o la conexión falla, registrar el error real como limitación y no modificar MySQL.

- [ ] **Step 4: Scan tracked files for secrets and review diff**

Revisar `git diff main...HEAD`, `git status`, archivos rastreados y patrones de claves/tokens/contraseñas reales. Las plantillas y textos de prueba ficticios no son secretos.

- [ ] **Step 5: Write the eleven-criterion evidence matrix**

Para Continuidad, Arquitectura, Persistencia, Repositorios, CRUD, Usuarios, Seguridad, Login, Instalación y ejecución, Calidad y Funcionamiento integral: indicar requisito, archivo, prueba, estado y limitación. No traducir pruebas aprobadas en promesa de nota.

- [ ] **Step 6: Commit verification evidence**

Run: `git add docs/EVALUACION_3_VERIFICACION.md && git commit -m "docs: documentar verificacion de la rubrica"`

- [ ] **Step 7: Final fresh verification**

Run: `.venv/bin/python -m pytest -q && .venv/bin/python -m compileall -q app.py main.py auxiliares datos negocio presentacion tests && git diff --check`

Expected: suite completa PASS, compilación exit 0 y diff limpio.
