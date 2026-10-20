"""Comprueba la conexión y las cuatro tablas sin cambiar datos de la tienda."""

from peewee import PeeweeException

from datos.configuracion import ConfiguracionBaseDatos
from datos.conexion import configurar_base_datos

TABLAS_REQUERIDAS = ("clientes", "productos", "pedidos", "detalles_pedido")


def main() -> int:
    base = None
    try:
        configuracion = ConfiguracionBaseDatos.desde_entorno()
        base = configurar_base_datos()
        base.connect(reuse_if_open=True)

        existentes = set(base.get_tables())
        faltantes = [tabla for tabla in TABLAS_REQUERIDAS if tabla not in existentes]
        print(f"Motor configurado: {configuracion.motor.upper()}")
        print(f"Base de datos: {configuracion.nombre if configuracion.motor == 'mysql' else configuracion.ruta_sqlite}")
        if faltantes:
            print("Faltan tablas: " + ", ".join(faltantes))
            return 1

        for tabla in TABLAS_REQUERIDAS:
            # Los nombres de las tablas provienen de una constante fija, no del usuario.
            cantidad = base.execute_sql(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            print(f"{tabla}: {cantidad} registros")

        print("Conexión correcta: se encontraron las cuatro tablas y se pudieron consultar.")
        return 0
    except (PeeweeException, ValueError, OSError) as error:
        print(f"No se pudo verificar la conexión: {error}")
        print("Compruebe el motor en .env, las credenciales y el servicio MySQL/XAMPP.")
        return 1
    finally:
        if base is not None and not base.is_closed():
            base.close()


if __name__ == "__main__":
    raise SystemExit(main())
