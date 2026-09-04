from pathlib import Path
from datetime import datetime
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "soporte_itop.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def _conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def inicializar_bd():
    if not SCHEMA_PATH.exists():
        raise RuntimeError(
            f"No se encontró el esquema de la base de datos: {SCHEMA_PATH}"
        )

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with _conexion() as conn:
        conn.executescript(schema)


def _texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()


def guardar_tickets(tickets):
    inicializar_bd()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nuevos = 0
    actualizados = 0
    sin_cambios = 0

    sql = """
        INSERT INTO tickets (
            referencia,
            clase_itop,
            itop_id,
            tipo,
            asunto,
            organizacion,
            reportado_por,
            analista,
            servicio,
            estado,
            estado_operativo,
            fecha_inicio,
            fecha_asignacion,
            fecha_solucion,
            fecha_cierre,
            fecha_fin,
            fecha_real_solucion,
            last_update_itop,
            sincronizado_en
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(referencia) DO UPDATE SET
            clase_itop = excluded.clase_itop,
            itop_id = excluded.itop_id,
            tipo = excluded.tipo,
            asunto = excluded.asunto,
            organizacion = excluded.organizacion,
            reportado_por = excluded.reportado_por,
            analista = excluded.analista,
            servicio = excluded.servicio,
            estado = excluded.estado,
            estado_operativo = excluded.estado_operativo,
            fecha_inicio = excluded.fecha_inicio,
            fecha_asignacion = excluded.fecha_asignacion,
            fecha_solucion = excluded.fecha_solucion,
            fecha_cierre = excluded.fecha_cierre,
            fecha_fin = excluded.fecha_fin,
            fecha_real_solucion = excluded.fecha_real_solucion,
            last_update_itop = excluded.last_update_itop,
            sincronizado_en = excluded.sincronizado_en
    """

    with _conexion() as conn:
        for ticket in tickets:
            referencia = _texto(ticket.get("referencia"))
            if not referencia:
                continue

            anterior = conn.execute(
                "SELECT last_update_itop FROM tickets WHERE referencia = ?",
                (referencia,)
            ).fetchone()

            conn.execute(
                sql,
                (
                    referencia,
                    _texto(ticket.get("clase_itop")),
                    ticket.get("itop_id"),
                    _texto(ticket.get("tipo")),
                    _texto(ticket.get("asunto")),
                    _texto(ticket.get("organizacion")),
                    _texto(ticket.get("reportado_por")),
                    _texto(ticket.get("analista")),
                    _texto(ticket.get("servicio")),
                    _texto(ticket.get("estado")),
                    _texto(ticket.get("estado_operativo")),
                    ticket.get("fecha_inicio"),
                    ticket.get("fecha_asignacion"),
                    ticket.get("fecha_solucion"),
                    ticket.get("fecha_cierre"),
                    ticket.get("fecha_fin"),
                    ticket.get("fecha_real_solucion"),
                    ticket.get("last_update_itop"),
                    ahora,
                )
            )

            if anterior is None:
                nuevos += 1
            elif anterior["last_update_itop"] == ticket.get("last_update_itop"):
                sin_cambios += 1
            else:
                actualizados += 1

    return {
        "nuevos": nuevos,
        "actualizados": actualizados,
        "sin_cambios": sin_cambios,
        "procesados": nuevos + actualizados + sin_cambios,
    }


def obtener_tickets(tipo=None):
    inicializar_bd()

    sql = """
        SELECT
            referencia,
            clase_itop,
            itop_id,
            tipo,
            asunto,
            organizacion,
            reportado_por,
            analista,
            servicio,
            estado,
            estado_operativo,
            fecha_inicio,
            fecha_asignacion,
            fecha_solucion,
            fecha_cierre,
            fecha_fin,
            fecha_real_solucion,
            last_update_itop
        FROM tickets
    """
    parametros = []

    if tipo:
        sql += " WHERE tipo = ?"
        parametros.append(tipo)

    sql += " ORDER BY fecha_inicio DESC, referencia DESC"

    with _conexion() as conn:
        filas = conn.execute(sql, parametros).fetchall()

    return [dict(fila) for fila in filas]


def obtener_ultima_actualizacion_itop(clase_itop):
    inicializar_bd()
    with _conexion() as conn:
        fila = conn.execute(
            """
            SELECT ultima_actualizacion_itop
            FROM sync_control
            WHERE clase_itop = ?
            """,
            (clase_itop,)
        ).fetchone()

    if not fila:
        return None

    return fila["ultima_actualizacion_itop"]


def guardar_control_sync(
    clase_itop,
    ultima_actualizacion_itop,
    cantidad_ultima_sync,
):
    inicializar_bd()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _conexion() as conn:
        conn.execute(
            """
            INSERT INTO sync_control (
                clase_itop,
                ultima_actualizacion_itop,
                ultima_sincronizacion,
                cantidad_ultima_sync
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(clase_itop) DO UPDATE SET
                ultima_actualizacion_itop = excluded.ultima_actualizacion_itop,
                ultima_sincronizacion = excluded.ultima_sincronizacion,
                cantidad_ultima_sync = excluded.cantidad_ultima_sync
            """,
            (
                clase_itop,
                ultima_actualizacion_itop,
                ahora,
                int(cantidad_ultima_sync),
            )
        )


def estado_sincronizacion():
    inicializar_bd()

    with _conexion() as conn:
        controles = conn.execute(
            """
            SELECT
                clase_itop,
                ultima_actualizacion_itop,
                ultima_sincronizacion,
                cantidad_ultima_sync
            FROM sync_control
            ORDER BY clase_itop
            """
        ).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) AS cantidad FROM tickets"
        ).fetchone()["cantidad"]

    filas = [dict(fila) for fila in controles]
    ultima = max(
        (fila["ultima_sincronizacion"] for fila in filas),
        default=None,
    )

    return {
        "ultima_sincronizacion": ultima,
        "total_tickets": int(total),
        "clases": filas,
    }
