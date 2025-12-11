# Esquema de la base de datos retail

## Tabla `categorias`
- `id` (NUMBER): identificador de la categoría.
- `nombre` (VARCHAR2): nombre de la categoría (Bebidas, Comida, Limpieza, etc.).

## Tabla `productos`
- `id` (NUMBER): identificador del producto.
- `nombre` (VARCHAR2): nombre del producto.
- `categoria_id` (NUMBER): FK a `categorias.id`.
- `precio` (NUMBER(10,2)): precio unitario del producto en euros.

## Tabla `tiendas`
- `id` (NUMBER): identificador de la tienda.
- `nombre` (VARCHAR2): nombre comercial de la tienda.
- `ciudad` (VARCHAR2): ciudad donde se encuentra la tienda.

## Tabla `ventas`
- `id` (NUMBER): identificador de la venta.
- `fecha` (DATE): fecha de la venta.
- `producto_id` (NUMBER): FK a `productos.id`.
- `tienda_id` (NUMBER): FK a `tiendas.id`.
- `cantidad` (NUMBER): unidades vendidas.
- `total` (NUMBER(10,2)): importe total de la venta (cantidad * precio).
