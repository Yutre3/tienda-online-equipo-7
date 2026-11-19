-- Ejecute como administrador después de cambiar la clave de ejemplo.
CREATE USER IF NOT EXISTS 'tienda_app'@'localhost'
    IDENTIFIED BY 'CAMBIAR_CLAVE_ANTES_DE_USAR';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
    ON tienda_online.* TO 'tienda_app'@'localhost';

FLUSH PRIVILEGES;
