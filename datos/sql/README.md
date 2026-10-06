# Base de datos de la tienda en línea

Esta carpeta cumple la misma función que `datos/sql` en el proyecto del
profesor: conserva dentro de Git la definición reproducible de la base.

`001_esquema.sql` crea la base `tienda_online` y las tablas `clientes`,
`productos`, `pedidos` y `detalles_pedido`, con claves primarias, tres claves
foráneas, restricciones e índices.

La forma recomendada de instalarla es desde la raíz del proyecto:

```bash
python -m scripts.crear_base_datos
```

También puede importarse `001_esquema.sql` desde phpMyAdmin. No se guardan aquí
contraseñas ni datos personales. Los cambios futuros del esquema deben añadirse
como nuevos archivos numerados, por ejemplo `002_nombre_del_cambio.sql`, sin
modificar datos existentes manualmente.
