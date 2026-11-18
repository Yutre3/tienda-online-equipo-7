USE tienda_online;

INSERT INTO paises (pais, nacionalidad, iso2, iso3, habilitado) VALUES
    ('Chile', 'Chilena', 'CL', 'CHL', TRUE)
ON DUPLICATE KEY UPDATE
    nacionalidad = VALUES(nacionalidad),
    habilitado = VALUES(habilitado);

INSERT INTO clientes (nombre, correo) VALUES
    ('Cliente de demostración', 'cliente@ejemplo.cl')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

INSERT INTO productos (sku, nombre, descripcion, precio_centavos, stock) VALUES
    ('TEC-001', 'Teclado mecánico', 'Teclado USB con iluminación', 3999000, 10),
    ('MOU-001', 'Mouse óptico', 'Mouse USB de cinco botones', 1299000, 20),
    ('AUD-001', 'Audífonos', 'Audífonos con micrófono', 2499000, 15)
ON DUPLICATE KEY UPDATE
    nombre = VALUES(nombre),
    descripcion = VALUES(descripcion),
    precio_centavos = VALUES(precio_centavos),
    stock = VALUES(stock);
