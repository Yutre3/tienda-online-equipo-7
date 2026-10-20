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
    class TiendaServicio {
        +registrar_cliente(Cliente cliente)
        +registrar_producto(Producto producto)
        +crear_pedido(int cliente_id)
        +agregar_producto(int pedido_id, int producto_id, int cantidad)
        +confirmar_pedido(int pedido_id)
        +cancelar_pedido(int pedido_id)
    }
    class RepositorioClientes
    class RepositorioProductos
    class RepositorioPedidos

    Entidad <|-- Cliente
    Entidad <|-- Producto
    Entidad <|-- Pedido
    Entidad <|-- DetallePedido
    Cliente "1" --> "0..*" Pedido : realiza
    Pedido "1" *-- "0..*" DetallePedido : contiene
    Producto "1" --> "0..*" DetallePedido : referencia
    Pedido --> EstadoPedido
    TiendaServicio --> RepositorioClientes
    TiendaServicio --> RepositorioProductos
    TiendaServicio --> RepositorioPedidos
    RepositorioClientes --> Cliente
    RepositorioProductos --> Producto
    RepositorioPedidos --> Pedido
```

## Correspondencia con la base de datos

`Cliente`, `Producto`, `Pedido` y `DetallePedido` se traducen respectivamente a las tablas `clientes`, `productos`, `pedidos` y `detalles_pedido`. `Pedido.cliente` se implementa con la clave foránea `cliente_id`; cada detalle contiene `pedido_id` y `producto_id`. La combinación de pedido y producto es única, por lo que agregar el mismo producto acumula la cantidad en una sola línea.
