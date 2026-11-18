# Diagrama UML — Tienda en línea

El diagrama muestra la herencia, asociaciones y dependencias principales implementadas. Las entidades encapsulan validaciones; los servicios coordinan reglas y los repositorios aíslan la persistencia Peewee.

```mermaid
classDiagram
    class Entidad {
        -int id
        +asignar_id(int identificador)
    }
    class Cliente {
        -str nombre
        -str correo
        +datetime creado_en
    }
    class Producto {
        -str sku
        -str nombre
        +str descripcion
        -int precio_centavos
        -int stock
        +descontar_stock(int cantidad)
        +reponer_stock(int cantidad)
    }
    class Pedido {
        +EstadoPedido estado
        +list detalles
        +int total_centavos
        +agregar_detalle(DetallePedido detalle)
        +quitar_detalle(int producto_id)
        +cambiar_estado(EstadoPedido estado)
    }
    class DetallePedido {
        +int cantidad
        +int precio_unitario_centavos
        +int subtotal_centavos
    }
    class EstadoPedido {
        <<enumeration>>
        CREADO
        CONFIRMADO
        CANCELADO
    }
    class PaisModelo {
        +int id_pais
        +str pais
        +str nacionalidad
        +str iso2
        +str iso3
        +bool habilitado
    }
    class UsuarioModelo {
        +int id_usuario
        +str rut
        +str nombre
        +str apellido
        +str correo
        +date fecha_nacimiento
        +int genero
        +bool habilitado
        +str password
    }
    class TiendaServicio {
        +listar_paises(str nombre)
        +registrar_usuario(...)
        +listar_usuarios(bool habilitado)
        +actualizar_usuario(str rut, ...)
        +deshabilitar_usuario(str rut)
        +registrar_cliente(Cliente cliente)
        +registrar_producto(Producto producto)
        +crear_pedido(int cliente_id)
        +agregar_producto(int pedido_id, int producto_id, int cantidad)
        +confirmar_pedido(int pedido_id)
        +cancelar_pedido(int pedido_id)
    }
    class RepositorioClientes
    class RepositorioPaises
    class RepositorioProductos
    class RepositorioPedidos
    class RepositorioUsuarios

    Entidad <|-- Cliente
    Entidad <|-- Producto
    Entidad <|-- Pedido
    Entidad <|-- DetallePedido
    Cliente "1" --> "0..*" Pedido : realiza
    Pedido "1" *-- "0..*" DetallePedido : contiene
    Producto "1" --> "0..*" DetallePedido : referencia
    Pedido --> EstadoPedido
    PaisModelo "1" --> "0..*" UsuarioModelo : nacionalidad
    TiendaServicio --> RepositorioPaises
    TiendaServicio --> RepositorioUsuarios
    TiendaServicio --> RepositorioClientes
    TiendaServicio --> RepositorioProductos
    TiendaServicio --> RepositorioPedidos
    RepositorioClientes --> Cliente
    RepositorioPaises --> PaisModelo
    RepositorioProductos --> Producto
    RepositorioPedidos --> Pedido
    RepositorioUsuarios --> UsuarioModelo
```

## Correspondencia con la base de datos

`PaisModelo`, `UsuarioModelo`, `Cliente`, `Producto`, `Pedido` y `DetallePedido` se traducen respectivamente a las tablas `paises`, `usuarios`, `clientes`, `productos`, `pedidos` y `detalles_pedido`. `UsuarioModelo.pais` referencia `paises.id_pais`; `Pedido.cliente` se implementa con la clave foránea `cliente_id`; cada detalle contiene `pedido_id` y `producto_id`. La combinación de pedido y producto es única, por lo que agregar el mismo producto acumula la cantidad en una sola línea.
