# Diseño de cumplimiento de la Evaluación 3

## Intención

Completar la tienda en línea del Grupo 7 sobre el proyecto existente, conservando el CRUD y las reglas de inventario de la Evaluación 2. El resultado debe demostrar los once criterios de la rúbrica mediante estructura, código ejecutable, pruebas y documentación, sin prometer una calificación académica.

## Objetivos

- Incorporar el punto de entrada oficial `main.py` sin duplicar la inicialización que seguirá viviendo en `app.py`.
- Centralizar todos los modelos en `datos/model_base.py:ModelBase` y conservar el alias `ModeloBase`.
- Hacer canónicos los repositorios basados en funciones dentro de `datos/repositorio/` para clientes, productos, pedidos, usuarios y países.
- Conservar las clases `Repositorio*` como adaptadores de compatibilidad que delegan en las funciones, sin repetir consultas.
- Exigir el flujo Aplicación → Login → Validación → Menú en `main.py` y `app.py`.
- Permitir cerrar sesión y volver al login, o cancelar el login y salir mediante una decisión acotada.
- Crear el primer usuario solo cuando la tabla de usuarios esté completamente vacía.
- Si existen cuentas pero ninguna puede acceder, impedir un alta alternativa y orientar al procedimiento local de recuperación.
- Conservar SQLite y MySQL, las seis tablas, las migraciones conservadoras y todo el CRUD actual.
- Actualizar README, Visual Studio Code y pruebas para que el recorrido oficial use `python main.py`.

## No objetivos y límites

- No agregar roles, permisos, servidores, API, interfaz gráfica ni autenticación avanzada.
- No borrar ni recrear tablas, bases de datos, diagramas, scripts SQL o aportes existentes.
- No cambiar las reglas de estados, totales o stock de los pedidos.
- No guardar ni publicar contraseñas, claves, cookies o credenciales de MySQL.
- No afirmar que MySQL funciona sin una conexión real con credenciales locales autorizadas.

## Arquitectura decidida

### Modelos

`datos/model_base.py` definirá `ModelBase(peewee.Model)` con `base_datos_proxy`. `ModeloBase = ModelBase` será un alias de compatibilidad. Los seis modelos importarán y heredarán de esa misma clase; no existirá una segunda configuración de Peewee.

### Repositorios

El paquete singular obligatorio `datos/repositorio/` contendrá módulos por entidad. Las funciones serán la implementación canónica y realizarán las consultas Peewee. El paquete histórico `datos/repositorios/` permanecerá como fachada compatible: sus clases llamarán a las funciones nuevas y no contendrán consultas duplicadas.

Las funciones de guardado usarán instancias de modelo y `save()`. Las funciones de pedidos conservarán las operaciones atómicas, bloqueo de fila en MySQL, reposición de stock y restricciones actuales mediante los servicios ya existentes. El descuento condicional de stock continuará como una actualización SQL aritmética y atómica: convertirla en una lectura seguida de `save()` debilitaría la protección contra concurrencia.

### Autenticación e inicio controlado

`app.py` seguirá siendo responsable de configurar, conectar y cerrar la base. Expondrá un flujo de aplicación reutilizable que:

1. comprueba el estado de las cuentas;
2. si no existe ninguna fila de usuario, ejecuta una sola preparación inicial mediante el formulario y validaciones existentes;
3. si hay filas pero ninguna cuenta habilitada posee un hash bcrypt válido, se detiene y muestra el comando local de recuperación; si todas están deshabilitadas, informa expresamente que cambiar una clave no habilita una cuenta;
4. solicita login con `login_usuario()`;
5. solo tras una autenticación correcta abre `menu_principal()`;
6. al elegir `0`, cierra la sesión, vuelve a evaluar las cuentas y regresa al login;
7. al cancelar el login, ofrece reintentar o terminar sin un bucle infinito.

El procedimiento local de recuperación seleccionará una cuenta existente por correo, solicitará una nueva contraseña oculta y reemplazará únicamente su hash. No creará cuentas ni habilitará cuentas deshabilitadas.

La preparación inicial exige al menos un país habilitado. En la ejecución normal SQLite se conserva la carga idempotente de Chile ya existente; si una base controlada no contiene países habilitados, la aplicación terminará con una explicación y no entrará en un formulario imposible de completar.

### Compatibilidad

`main.py` solo delegará en `app.main()`. `python app.py` conservará el mismo flujo oficial. Las importaciones antiguas de modelos y repositorios seguirán disponibles. La presentación y los servicios mantendrán sus contratos de CRUD; solo cambiará el acceso al menú desde el punto de entrada.

## Verificación

- Pruebas unitarias e integrales con SQLite temporal para modelos, funciones de repositorio, CRUD, inventario, login, alta inicial, recuperación, logout, persistencia y ambos puntos de entrada.
- Ejecución completa con `python -m pytest -q`, compilación, validación JSON de `.vscode`, `git diff --check`, búsqueda de secretos y arranque controlado.
- Verificación MySQL solo si el `.env` local permite conectarse sin exponer credenciales.
- Revisión final criterio por criterio con archivos y pruebas como evidencia.
