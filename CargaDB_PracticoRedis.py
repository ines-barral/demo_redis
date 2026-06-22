import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import time


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rootpassword",
    "database": "practico1",
    "autocommit": False,
}


CANT_PERSONAS = 100_000
CANT_VIDEOJUEGOS = 100_000
CANT_COMPRAS = 800_000
BATCH_SIZE = 5_000

TIPOS_VIDEOJUEGO = [
    "accion",
    "aventura",
    "estrategia",
    "rpg",
    "deportes",
    "simulacion",
    "terror",
    "puzzle",
]


def conectar():
    return mysql.connector.connect(**DB_CONFIG)


def limpiar_tablas(cursor, conn):
    print("Limpiando tablas...")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE COMPRA")
    cursor.execute("TRUNCATE TABLE VIDEOJUEGOS")
    cursor.execute("TRUNCATE TABLE PERSONAS")
    cursor.execute("TRUNCATE TABLE TIPO_VIDEOJUEGOS")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    conn.commit()


def insertar_tipos(cursor, conn):
    print("Insertando tipos de videojuegos...")

    sql = """
        INSERT INTO TIPO_VIDEOJUEGOS (tipo)
        VALUES (%s)
    """

    datos = [(tipo,) for tipo in TIPOS_VIDEOJUEGO]

    cursor.executemany(sql, datos)
    conn.commit()


def insertar_personas(cursor, conn):
    print("Insertando PERSONAS...")

    sql = """
        INSERT INTO PERSONAS
            (email, password, nombre, apellido, fecha_nacimiento)
        VALUES
            (%s, %s, %s, %s, %s)
    """

    fecha_base = date(1980, 1, 1)
    batch = []
    inicio = time.perf_counter()

    for i in range(1, CANT_PERSONAS + 1):
        email = f"persona{i}@mail.com"
        password = f"password{i}"
        nombre = f"Nombre{i}"
        apellido = f"Apellido{i}"
        fecha_nacimiento = fecha_base + timedelta(days=i % 12000)

        batch.append((email, password, nombre, apellido, fecha_nacimiento))

        if len(batch) == BATCH_SIZE:
            cursor.executemany(sql, batch)
            conn.commit()
            batch.clear()

        if i % 50_000 == 0:
            print(f"  PERSONAS insertadas: {i:,}")

    if batch:
        cursor.executemany(sql, batch)
        conn.commit()

    fin = time.perf_counter()
    print(f"PERSONAS listo. Tiempo: {fin - inicio:.2f} segundos")


def insertar_videojuegos(cursor, conn):
    print("Insertando VIDEOJUEGOS...")

    sql = """
        INSERT INTO VIDEOJUEGOS
            (nombre, dificultad, descripcion, costo, tipo)
        VALUES
            (%s, %s, %s, %s, %s)
    """

    batch = []
    inicio = time.perf_counter()

    for i in range(1, CANT_VIDEOJUEGOS + 1):
        nombre = f"Videojuego{i}"
        dificultad = str((i % 5) + 1)
        descripcion = f"Descripcion del videojuego {i}"
        costo = round(10 + (i % 90) + 0.99, 2)
        tipo = TIPOS_VIDEOJUEGO[i % len(TIPOS_VIDEOJUEGO)]

        batch.append((nombre, dificultad, descripcion, costo, tipo))

        if len(batch) == BATCH_SIZE:
            cursor.executemany(sql, batch)
            conn.commit()
            batch.clear()

        if i % 50_000 == 0:
            print(f"  VIDEOJUEGOS insertados: {i:,}")

    if batch:
        cursor.executemany(sql, batch)
        conn.commit()

    fin = time.perf_counter()
    print(f"VIDEOJUEGOS listo. Tiempo: {fin - inicio:.2f} segundos")


def insertar_compras(cursor, conn):
    print("Insertando COMPRA...")

    sql = """
        INSERT INTO COMPRA
            (id_compra, email, nombre_videojuego, nombre_expansion, valor, fecha)
        VALUES
            (%s, %s, %s, %s, %s, %s)
    """

    fecha_base = date(2022, 1, 1)
    batch = []
    inicio = time.perf_counter()

    for i in range(1, CANT_COMPRAS + 1):
        id_compra = i

        persona_id = ((i * 17) % CANT_PERSONAS) + 1
        videojuego_id = ((i * 31) % CANT_VIDEOJUEGOS) + 1

        email = f"persona{persona_id}@mail.com"
        nombre_videojuego = f"Videojuego{videojuego_id}"

        nombre_expansion = None
        valor = round(10 + (videojuego_id % 90) + 0.99, 2)

        fecha = fecha_base + timedelta(days=i % 1000)

        batch.append((
            id_compra,
            email,
            nombre_videojuego,
            nombre_expansion,
            valor,
            fecha
        ))

        if len(batch) == BATCH_SIZE:
            cursor.executemany(sql, batch)
            conn.commit()
            batch.clear()

        if i % 100_000 == 0:
            print(f"  COMPRAS insertadas: {i:,}")

    if batch:
        cursor.executemany(sql, batch)
        conn.commit()

    fin = time.perf_counter()
    print(f"COMPRA listo. Tiempo: {fin - inicio:.2f} segundos")


def main():
    try:
        conn = conectar()
        cursor = conn.cursor()

        limpiar_tablas(cursor, conn)

        insertar_tipos(cursor, conn)
        insertar_personas(cursor, conn)
        insertar_videojuegos(cursor, conn)
        insertar_compras(cursor, conn)

        cursor.close()
        conn.close()

        print("Carga finalizada correctamente.")

    except Error as e:
        print("Error al trabajar con MySQL:")
        print(e)


if __name__ == "__main__":
    main()