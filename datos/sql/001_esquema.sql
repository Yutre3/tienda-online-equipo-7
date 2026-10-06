-- Base de datos de la tienda en línea del Equipo 7.
-- Este archivo puede importarse directamente desde phpMyAdmin.

CREATE DATABASE IF NOT EXISTS tienda_online
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE tienda_online;

CREATE TABLE IF NOT EXISTS clientes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(120) NOT NULL,
    correo VARCHAR(190) NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_clientes_correo (correo),
    CONSTRAINT chk_clientes_nombre CHECK (CHAR_LENGTH(TRIM(nombre)) > 0),
    CONSTRAINT chk_clientes_correo CHECK (correo LIKE '%_@_%._%')
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS productos (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    precio_centavos BIGINT UNSIGNED NOT NULL,
    stock INT UNSIGNED NOT NULL DEFAULT 0,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_productos_nombre (nombre),
    CONSTRAINT chk_productos_nombre CHECK (CHAR_LENGTH(TRIM(nombre)) > 0),
    CONSTRAINT chk_productos_precio CHECK (precio_centavos > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pedidos (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    cliente_id BIGINT UNSIGNED NOT NULL,
    estado ENUM('CREADO', 'CONFIRMADO', 'CANCELADO') NOT NULL DEFAULT 'CREADO',
    total_centavos BIGINT UNSIGNED NOT NULL DEFAULT 0,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_pedidos_cliente (cliente_id),
    CONSTRAINT fk_pedidos_cliente FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalles_pedido (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    pedido_id BIGINT UNSIGNED NOT NULL,
    producto_id BIGINT UNSIGNED NOT NULL,
    cantidad INT UNSIGNED NOT NULL,
    precio_unitario_centavos BIGINT UNSIGNED NOT NULL,
    subtotal_centavos BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_detalle_pedido_producto (pedido_id, producto_id),
    KEY idx_detalles_producto (producto_id),
    CONSTRAINT fk_detalles_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedidos(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_detalles_producto FOREIGN KEY (producto_id)
        REFERENCES productos(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_detalles_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalles_precio CHECK (precio_unitario_centavos > 0),
    CONSTRAINT chk_detalles_subtotal CHECK (subtotal_centavos > 0)
) ENGINE=InnoDB;
