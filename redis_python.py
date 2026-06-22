import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import json
import time

import redis


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rootpassword",
    "database": "practico1",
    "autocommit": True,
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": "passwordBernie",
    "decode_responses": True,
}

cliente_redis = redis.Redis(**REDIS_CONFIG)
TIEMPO_EXPIRACION = 300

sql = """
SELECT
    v.nombre,
    v.tipo,
    v.dificultad,
    v.costo,
    COUNT(c.id_compra) AS cantidad_compras,
    SUM(c.valor) AS recaudacion_total
FROM VIDEOJUEGOS v
JOIN COMPRA c
    ON c.nombre_videojuego = v.nombre
WHERE v.tipo = %s
GROUP BY
    v.nombre,
    v.tipo,
    v.dificultad,
    v.costo
ORDER BY
    cantidad_compras DESC,
    recaudacion_total DESC
LIMIT 10
"""


def conectar_mysql():
    return mysql.connector.connect(**DB_CONFIG)


def _serializar_resultado(resultado):
    return json.dumps(resultado, default=str)


def _deserializar_resultado(resultado_cache):
    return json.loads(resultado_cache)


def top_videojuegos(tipo_videojuego):
    clave_redis = f"ranking_videojuegos_tipo:{tipo_videojuego}"
    print("Buscando en cache...")
    inicio = time.perf_counter()
    resultado_cache = cliente_redis.get(clave_redis)
    fin = time.perf_counter()


    if resultado_cache:
        print("CACHE HIT")
        print(f"Tiempo de consulta: {fin-inicio:.6f} segundos")
        return _deserializar_resultado(resultado_cache)

    print("CACHE MISS")

    try:
        conn = conectar_mysql()
        cursor = conn.cursor(dictionary=True)

        inicio = time.perf_counter()
        cursor.execute(sql, (tipo_videojuego,))
        resultado_mysql = cursor.fetchall()
        fin = time.perf_counter()

        print(f"Tiempo de consulta: {fin-inicio:.6f} segundos")

        cliente_redis.setex(
            clave_redis,
            TIEMPO_EXPIRACION,
            _serializar_resultado(resultado_mysql),
        )

        cursor.close()
        conn.close()

        return resultado_mysql
    except Error as e:
        print("Error al consultar MySQL:")
        print(e)
        return None


resultado = top_videojuegos("accion")
print("Resultado:")
print(resultado)