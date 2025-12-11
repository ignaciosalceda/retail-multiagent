# scripts/seed_oracle.py

import random
from datetime import datetime, timedelta

import oracledb
from faker import Faker

fake = Faker("es_ES")

# -----------------------------
# CONFIGURACIÓN DE CONEXIÓN
# -----------------------------
ORACLE_USER = "retail"
ORACLE_PASSWORD = "retail"
ORACLE_DSN = "localhost:1521/XEPDB1"

NUM_CATEGORIAS = 6
NUM_TIENDAS = 12
NUM_PRODUCTOS = 80
NUM_VENTAS = 8000


# -----------------------------
# CONEXIÓN
# -----------------------------
def get_conn():
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )


# -----------------------------
# INSERT CATEGORIAS
# -----------------------------
def insert_categorias(cur):
    categorias = [
        "Bebidas", "Comida", "Limpieza",
        "Higiene", "Snacks", "Mascotas"
    ]

    for c in categorias:
        cur.execute("INSERT INTO categorias (nombre) VALUES (:1)", [c])

    print(f"✅ {len(categorias)} categorías insertadas")


# -----------------------------
# INSERT TIENDAS
# -----------------------------
def insert_tiendas(cur):
    tiendas = []

    for _ in range(NUM_TIENDAS):
        tiendas.append((
            fake.company(),
            fake.city()
        ))

    cur.executemany(
        "INSERT INTO tiendas (nombre, ciudad) VALUES (:1, :2)",
        tiendas
    )

    print(f"✅ {len(tiendas)} tiendas insertadas")


# -----------------------------
# INSERT PRODUCTOS
# -----------------------------
def insert_productos(cur):
    productos = []

    for _ in range(NUM_PRODUCTOS):
        productos.append((
            fake.word().capitalize(),
            random.randint(1, 6),  # categorias
            round(random.uniform(0.5, 25), 2)
        ))

    cur.executemany(
        "INSERT INTO productos (nombre, categoria_id, precio) VALUES (:1, :2, :3)",
        productos
    )

    print(f"✅ {len(productos)} productos insertados")


# -----------------------------
# INSERT VENTAS
# -----------------------------
def insert_ventas(cur):
    ventas = []

    start_date = datetime(2023, 1, 1)

    for _ in range(NUM_VENTAS):
        fecha = start_date + timedelta(days=random.randint(0, 450))
        producto_id = random.randint(1, NUM_PRODUCTOS)
        tienda_id = random.randint(1, NUM_TIENDAS)
        cantidad = random.randint(1, 12)
        precio = round(random.uniform(1, 30), 2)
        total = round(cantidad * precio, 2)

        ventas.append((
            fecha,
            producto_id,
            tienda_id,
            cantidad,
            total
        ))

    cur.executemany(
        """
        INSERT INTO ventas (fecha, producto_id, tienda_id, cantidad, total)
        VALUES (:1, :2, :3, :4, :5)
        """,
        ventas
    )

    print(f"✅ {len(ventas)} ventas insertadas")


# -----------------------------
# MAIN
# -----------------------------
def main():
    conn = get_conn()
    cur = conn.cursor()

    print("🧹 Limpiando tablas...")
    cur.execute("DELETE FROM ventas")
    cur.execute("DELETE FROM productos")
    cur.execute("DELETE FROM tiendas")
    cur.execute("DELETE FROM categorias")

    insert_categorias(cur)
    insert_tiendas(cur)
    insert_productos(cur)
    insert_ventas(cur)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Base de datos poblada correctamente")


if __name__ == "__main__":
    main()
