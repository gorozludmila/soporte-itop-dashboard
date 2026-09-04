from threading import Lock

from services.database import (
    guardar_control_sync,
    guardar_tickets,
    obtener_ultima_actualizacion_itop,
)
from services.itop_api import obtener_tickets_itop


_sync_lock = Lock()


CLASES = {
    "Incident": "Incidente",
    "UserRequest": "Requerimiento",
}


def _max_last_update(datos, anterior=None):
    valores = [
        str(x.get("last_update_itop")).strip()
        for x in datos
        if x.get("last_update_itop")
    ]

    if anterior:
        valores.append(anterior)

    return max(valores) if valores else anterior


def sincronizar_clase(clase_itop):
    if clase_itop not in CLASES:
        raise ValueError(f"Clase iTop no soportada: {clase_itop}")

    ultima = obtener_ultima_actualizacion_itop(clase_itop)

    datos = obtener_tickets_itop(
        clase_itop,
        modificados_desde=ultima,
    )

    resultado = guardar_tickets(datos)
    nuevo_marcador = _max_last_update(datos, ultima)

    guardar_control_sync(
        clase_itop,
        nuevo_marcador,
        len(datos),
    )

    return {
        "clase": clase_itop,
        "tipo": CLASES[clase_itop],
        "desde": ultima,
        "recibidos": len(datos),
        **resultado,
        "ultima_actualizacion_itop": nuevo_marcador,
    }


def sincronizar_todo():
    if not _sync_lock.acquire(blocking=False):
        raise RuntimeError("Ya hay una actualización de iTop en curso.")

    try:
        resultados = [
            sincronizar_clase("Incident"),
            sincronizar_clase("UserRequest"),
        ]

        return {
            "recibidos": sum(x["recibidos"] for x in resultados),
            "nuevos": sum(x["nuevos"] for x in resultados),
            "actualizados": sum(x["actualizados"] for x in resultados),
            "sin_cambios": sum(x["sin_cambios"] for x in resultados),
            "detalle": resultados,
        }
    finally:
        _sync_lock.release()
