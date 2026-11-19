-- Migración para instalaciones anteriores que ya tenían la tabla productos.
-- No ejecute este archivo en una instalación nueva creada con el DDL actual.
USE tienda_online;

SET @existe_sku = (
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'productos'
      AND column_name = 'sku'
);
SET @sentencia = IF(
    @existe_sku = 0,
    'ALTER TABLE productos ADD COLUMN sku VARCHAR(50) NULL AFTER id',
    'SELECT ''La columna SKU ya existe'''
);
PREPARE migracion FROM @sentencia;
EXECUTE migracion;
DEALLOCATE PREPARE migracion;

UPDATE productos
SET sku = CONCAT('LEGACY-', LPAD(id, 6, '0'))
WHERE sku IS NULL OR TRIM(sku) = '';

SET @existe_indice = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'productos'
      AND index_name = 'uq_productos_sku'
);
SET @sentencia = IF(
    @existe_indice = 0,
    'ALTER TABLE productos ADD UNIQUE KEY uq_productos_sku (sku)',
    'SELECT ''El índice SKU ya existe'''
);
PREPARE migracion FROM @sentencia;
EXECUTE migracion;
DEALLOCATE PREPARE migracion;

ALTER TABLE productos MODIFY sku VARCHAR(50) NOT NULL;
