# Integración final con el proyecto del profesor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar el PR #1, completar la presentación de usuarios y publicar una versión comprobada de la tienda en `main`.

**Architecture:** Se conserva la fachada `TiendaServicio`, los repositorios y modelos Peewee existentes. Los cambios nuevos se limitan a presentación, migración conservadora, pruebas y resolución semántica de las ramas.

**Tech Stack:** Python 3.14, Peewee, PyMySQL, SQLite, bcrypt, maskpass, PrettyTable, python-decouple, pytest y Git.

**Spec:** `docs/superpowers/specs/2026-11-19-integracion-final-profesor-design.md`

## Global Constraints

- Trabajar sólo en `Yutre3/tienda-online-equipo-7`.
- No usar `force-push`, `reset --hard` ni eliminar `feat/finalizar-tienda`.
- Mantener clientes, productos, inventario, pedidos, totales, documentación, UML y `.vscode/`.
- Mantener el login como preparación no funcional.
- Usar bases temporales en pruebas que escriben datos.

## Review Focus

- Una búsqueda inexistente debe mostrar un error controlado y devolver al menú.
- La baja de usuario debe pedir confirmación y conservar la fila.
- Una tabla `usuarios` antigua sin `password` debe conservar sus registros al migrar.
- La fusión no debe aceptar las eliminaciones de `.vscode`, pruebas o capas modulares hechas en la línea divergente de `main`.
- La publicación debe dejar `main` y `feat/finalizar-tienda` accesibles en el mismo remoto.

---

### Task 1: Integrar `main` sin perder trabajo

**Files:** archivos en conflicto informados por Git.

**Interfaces:** conserva la API pública y el árbol probado de `feat/finalizar-tienda` e incorpora el historial de `main`.

- [ ] Fusionar `origin/main` con `--no-commit` y revisar cada conflicto.
- [ ] Conservar la arquitectura modular, las pruebas, `.vscode/`, SQL, documentación y funcionalidades equivalentes de ambas ramas.
- [ ] Ejecutar `.venv/bin/python -m pytest -q`; resultado esperado: 86 pruebas aprobadas.
- [ ] Crear el commit de integración.

### Task 2: Búsquedas de usuarios en consola

**Files:**
- Modify: `presentacion/presentacion_usuario.py`
- Modify: `presentacion/menu.py`
- Test: `tests/test_presentacion_usuario.py`

**Interfaces:** produce `mostrar_usuario_por_rut(servicio, ...)` y `mostrar_usuario_por_correo(servicio, ...)`; consume `TiendaServicio.buscar_usuario_rut/correo`.

- [ ] Escribir pruebas que fallen porque las funciones y opciones todavía no existen.
- [ ] Ejecutar las pruebas específicas y confirmar el fallo esperado.
- [ ] Implementar ambas consultas reutilizando validaciones y `tabla_usuarios`.
- [ ] Añadir ambas acciones al submenú y ejecutar de nuevo las pruebas.

### Task 3: Migración conservadora de contraseña

**Files:**
- Modify: `datos/conexion.py`
- Test: `tests/test_usuarios.py`

**Interfaces:** `migrar_esquema()` añade `usuarios.password VARCHAR(60) NULL` sólo cuando la tabla existe y la columna falta.

- [ ] Crear una base temporal con una fila antigua y escribir la prueba de migración fallida.
- [ ] Confirmar que falla por columna ausente.
- [ ] Añadir la migración Peewee sin recrear ni vaciar la tabla.
- [ ] Confirmar que la fila, relaciones y valores originales permanecen.

### Task 4: Verificación integral

**Files:** sólo correcciones necesarias demostradas por pruebas.

**Interfaces:** aplicación ejecutable desde `app.py` y tareas de VS Code válidas.

- [ ] Ejecutar pruebas específicas y luego `.venv/bin/python -m pytest -q`.
- [ ] Ejecutar `compileall` y validar todos los JSON de `.vscode/`.
- [ ] Verificar SQLite en una base temporal y consultar MySQL sólo si las credenciales existentes permiten conexión.
- [ ] Ejecutar un recorrido de menú controlado sin escribir datos permanentes.

### Task 5: Publicación e integración del PR #1

**Files:** historial Git.

**Interfaces:** `origin/feat/finalizar-tienda` y `origin/main` actualizados sin eliminar ramas.

- [ ] Publicar los commits de la rama de desarrollo con `git push` normal.
- [ ] Integrar la rama en `main` mediante fusión no destructiva y publicar `main`.
- [ ] Consultar las referencias remotas y la página del PR para verificar el resultado final.
- [ ] Ejecutar un último punto de control de memoria con pruebas y SHA publicados.
