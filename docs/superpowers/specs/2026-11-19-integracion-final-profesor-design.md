# Diseño de integración final con el proyecto del profesor

## Propósito

Completar el único repositorio `Yutre3/tienda-online-equipo-7` conservando la tienda existente y adaptando los avances publicados hasta el commit `6b85132` de `baileytorch/IEI_N2_C2_POO`.

## Estado comprobado

- `feat/finalizar-tienda` ya implementa tres capas, POO, Peewee, MySQL/SQLite, PrettyTable, clientes, productos, inventario, pedidos y CRUD de usuarios.
- La línea base de la rama aprueba 86 pruebas.
- El PR #1 integra `feat/finalizar-tienda` en `main`, pero ambas ramas divergen desde `d07331b`.
- El último avance del profesor completa la baja lógica de usuarios, la búsqueda por correo y deja el login sólo en su captura inicial de correo.

## Resultado requerido

- Conservar las funcionalidades y archivos útiles de ambas ramas sin reconstruir el proyecto.
- Exponer en consola listado, registro, búsqueda por RUT, búsqueda por correo, modificación y deshabilitación confirmada de usuarios.
- Mantener contraseña oculta y hash bcrypt, RUT chileno, país, nacionalidad, fecha, género y correo validados.
- Mantener el login como función preparatoria que sólo solicita correo; no anunciar autenticación funcional.
- Crear o migrar tablas de forma conservadora, incluida la columna `usuarios.password` de instalaciones antiguas, sin borrar filas.
- Mantener `.env` fuera de Git, la configuración portable de Visual Studio Code y las pruebas sobre SQLite temporal.
- Publicar la rama de desarrollo, integrar el PR #1 sin `force-push`, actualizar `main` y no eliminar la rama.

## Límites

- No copiar módulos de libros, bibliotecas o préstamos.
- No almacenar secretos ni pedir contraseñas o tokens en el chat.
- No afirmar que MySQL fue probado si las credenciales locales no permiten conectarlo.
- No borrar datos ni sustituir la aplicación por otra implementación.

## Criterio de finalización

La integración termina cuando no quedan conflictos, la suite completa y la compilación aprueban, las configuraciones de VS Code son válidas, las verificaciones de base disponibles quedan documentadas y GitHub muestra `main` actualizado junto con la rama de desarrollo conservada.
