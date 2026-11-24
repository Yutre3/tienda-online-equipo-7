# Verificación de la Evaluación 3

Fecha de comprobación: 24 de noviembre de 2026.

Este documento relaciona la implementación con los once criterios informados para la Evaluación 3. Es evidencia técnica del proyecto y no una promesa de puntaje, porque la calificación corresponde al profesor.

## Resultado técnico reproducible

- `.venv/bin/python -m pytest -q`: **125 pruebas aprobadas** (la duración depende del equipo).
- `.venv/bin/python -m compileall -q app.py main.py auxiliares datos negocio presentacion tests`: código de salida 0.
- `git diff --check`: sin errores de espacios.
- Búsqueda de marcadores de conflicto: sin resultados.
- `.vscode/*.json`: cuatro archivos analizados correctamente como JSON.
- SQLite temporal: seis tablas creadas y consultadas; el segundo inicio devolvió los mismos conteos que el primero.
- Prueba focalizada de login/logout y prueba de reapertura SQLite: 2 aprobadas.
- `datos/tienda_online.db`: hash Git idéntico antes y después de las verificaciones; no aparece en el diff.
- Búsqueda en archivos rastreados: no se encontraron patrones de claves privadas, tokens de GitHub/OpenAI/Google ni `.env` rastreado.
- MySQL: no se ejecutó una conexión real porque no existe `.env` local con credenciales autorizadas. El código, dependencia, configuración de ejemplo y scripts permanecen presentes, pero esta verificación extremo a extremo queda pendiente.

## Matriz de los 11 criterios

| N.º | Criterio | Implementación y archivo que la demuestra | Prueba o verificación | Estado y limitación |
| --- | --- | --- | --- | --- |
| 1 | Continuidad del proyecto | Se conservaron `app.py`, entidades, servicios, menús, UML, SQL y pruebas de la Evaluación 2. `main.py` delega en el flujo existente. | Suite completa; `tests/test_puntos_entrada.py`; diff sin cambios en la base rastreada. | Completo dentro del alcance. No se reconstruyó la tienda. |
| 2 | Arquitectura | Capas `datos/`, `negocio/`, `presentacion/`, `auxiliares/`; `datos/model_base.py`; modelos en `datos/modelos/`; funciones en `datos/repositorio/`; compatibilidad en `datos/repositorios/`. | `tests/test_arquitectura_evaluacion3.py` y pruebas de importación de repositorios. | Completo. `ModelBase` es único y usa la conexión compartida. |
| 3 | Persistencia | `datos/conexion.py` configura SQLite o MySQL, crea seis tablas de forma segura y conserva migraciones idempotentes de SKU/password. | SQLite temporal con seis tablas; `tests/test_verificar_base_datos.py`; pruebas de migración y reapertura. | SQLite completo. MySQL implementado, pero la conexión real queda pendiente por falta de `.env` autorizado. |
| 4 | Repositorios | `datos/repositorio/clientes.py`, `productos.py`, `pedidos.py`, `usuarios.py`, `paises.py` implementan funciones Peewee. Las clases anteriores solo delegan. | `tests/test_repositorios_funcionales.py` comprueba funciones, CRUD real y uso de `save()`; `tests/test_repositorios.py` comprueba compatibilidad. | Completo. El descuento de stock conserva su `UPDATE` condicional atómico. |
| 5 | CRUD | Clientes, productos y pedidos siguen expuestos en `presentacion/menu.py` y coordinados por `negocio/servicios.py`. | `tests/test_repositorios.py`, `tests/test_servicios.py`, `tests/test_presentacion.py`; reglas de detalle, estados, cancelación y eliminación. | Completo dentro de las operaciones definidas. |
| 6 | Usuarios | Registro, tres listados, búsqueda por RUT/correo, actualización y baja lógica en `negocio/servicios.py`, `presentacion/presentacion_usuario.py` y repositorio funcional. | `tests/test_usuarios.py`, `tests/test_presentacion_usuario.py`, `tests/test_validaciones_usuario.py`. | Completo. La baja conserva físicamente la fila. |
| 7 | Seguridad | `maskpass` con respaldo `getpass`, hash bcrypt textual de 60 caracteres, verificación `bcrypt.checkpw()`, mensaje genérico y hash ficticio para rutas rechazadas. `.env` está ignorado. | Casos de hash/no texto plano, usuario inexistente, clave errónea, deshabilitado, hash inválido y comprobación temporal en `tests/test_usuarios.py`; escaneo de secretos. | Completo para la aplicación local. |
| 8 | Login | `app.ejecutar_aplicacion()` impone Aplicación → Login → Validación → Menú; `login_usuario()` y `TiendaServicio.autenticar_usuario()` se reutilizan. Logout reevalúa cuentas. | `tests/test_flujo_autenticacion.py`: acceso correcto, rechazos, cancelación, logout, última cuenta y ausencia de ruta de login dentro del menú. | Completo. No existe una ruta normal desde `main.py` al menú sin autenticación. |
| 9 | Instalación y ejecución | `README.md`, `requirements.txt`, `.env.example`, `.vscode/`, `main.py`; alta inicial segura y `python -m auxiliares.recuperar_acceso`. | `tests/test_configuracion_entrega.py`; `tests/test_puntos_entrada.py` ejecuta `main.py` y `app.py` en subprocesos controlados. | Completo para SQLite/VS Code. MySQL requiere configuración local del evaluador. |
| 10 | Calidad del código | Tipos, separación de capas, funciones canónicas sin duplicar consultas, adaptadores compatibles, errores de dominio y pruebas de regresión. | 125 pruebas, `compileall`, JSON válido, `git diff --check`, ausencia de conflictos y revisión de secretos. | Completo según comprobaciones automáticas; queda sujeta a revisión académica. |
| 11 | Funcionamiento integral | Inicio, preparación segura, login, CRUD, pedidos, inventario, logout y persistencia están conectados por `app.py`/`main.py`. | Arranque SQLite temporal; suite integral; pruebas concurrentes de cancelación/stock; reapertura de base y compatibilidad de entradas. | Completo en SQLite. La ejecución integral MySQL no fue observable sin credenciales locales. |

## Preparación inicial y recuperación

- Con cero filas en `usuarios`, `preparar_primer_usuario()` usa las validaciones y formulario existentes y almacena bcrypt.
- Con cualquier fila existente, el alta inicial queda cerrada.
- Con cuentas habilitadas pero hashes inválidos, la aplicación orienta al comando local y no crea otra cuenta.
- Con todas las cuentas deshabilitadas, informa que cambiar una clave no habilita una cuenta.
- La recuperación modifica solo `password`; conserva identidad, datos y estado.

## Pendiente externo

Para cerrar la única limitación técnica observada, un integrante debe crear un `.env` local no rastreado con credenciales MySQL/MariaDB autorizadas, iniciar el servidor y ejecutar:

```bash
python verificar_base_datos.py
python -m pytest -q
```

No deben copiarse las credenciales a Git, al README, a una incidencia ni a la salida de pruebas.
