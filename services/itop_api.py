import os
import json
import requests

from dotenv import load_dotenv


load_dotenv()

ITOP_API_URL = os.getenv("ITOP_API_URL")
ITOP_TOKEN = os.getenv("ITOP_TOKEN")

# MGeIP#STG # Departamento Unidad de Gestión Digital
PROVEEDOR_ID = 468


ESTADOS = {
    "new": "Nuevo",
    "dispatched": "Despachado",
    "redispatched": "Redespachado",
    "assigned": "Asignado",
    "pending": "Pendiente",
    "resolved": "Solucionado",
    "closed": "Cerrado",
}


def traducir_estado(valor):
    if not valor:
        return ""

    valor = str(valor).strip()
    return ESTADOS.get(valor.lower(), valor)


def llamar_itop(payload):
    if not ITOP_API_URL:
        raise RuntimeError("Falta ITOP_API_URL en el archivo .env")

    if not ITOP_TOKEN:
        raise RuntimeError("Falta ITOP_TOKEN en el archivo .env")

    headers = {
        "Auth-Token": ITOP_TOKEN,
        "Accept": "application/json",
    }

    datos = {
        "json_data": json.dumps(payload),
    }

    respuesta = requests.post(
        ITOP_API_URL,
        headers=headers,
        data=datos,
        timeout=120,
    )

    respuesta.raise_for_status()
    resultado = respuesta.json()

    if resultado.get("code") != 0:
        raise RuntimeError(
            f"Error iTop: {resultado.get('code')} - "
            f"{resultado.get('message')}"
        )

    return resultado


def _escapar_oql(valor):
    return str(valor).replace("'", "''")


def obtener_tickets_itop(clase, modificados_desde=None):
    if clase not in ["Incident", "UserRequest"]:
        raise ValueError(
            "Clase inválida. Debe ser Incident o UserRequest"
        )

    condiciones = [f"s.org_id = {PROVEEDOR_ID}"]

    # Usamos >= a propósito: si varios tickets comparten exactamente
    # el mismo segundo de last_update, se vuelven a leer en la próxima
    # sincronización y el UPSERT de SQLite evita duplicados.
    if modificados_desde:
        fecha = _escapar_oql(modificados_desde)
        condiciones.append(f"t.last_update >= '{fecha}'")

    consulta = f"""
        SELECT {clase} AS t
        JOIN Service AS s ON t.service_id = s.id
        WHERE {' AND '.join(condiciones)}
    """

    resultado = llamar_itop({
        "operation": "core/get",
        "class": clase,
        "key": consulta,
        "output_fields": ",".join([
            "ref",
            "title",
            "org_id_friendlyname",
            "caller_id_friendlyname",
            "agent_id_friendlyname",
            "service_name",
            "status",
            "start_date",
            "assignment_date",
            "resolution_date",
            "close_date",
            "end_date",
            "last_update",
        ]),
    })

    objetos = resultado.get("objects") or {}
    filas = []

    for objeto in objetos.values():
        f = objeto.get("fields", {})

        filas.append({
            "itop_id": objeto.get("key"),
            "clase_itop": clase,
            "tipo": "Incidente" if clase == "Incident" else "Requerimiento",
            "referencia": f.get("ref", ""),
            "asunto": f.get("title", ""),
            "organizacion": f.get("org_id_friendlyname", ""),
            "reportado_por": f.get("caller_id_friendlyname", ""),
            "analista": f.get("agent_id_friendlyname", ""),
            "servicio": f.get("service_name", ""),
            "estado": traducir_estado(f.get("status", "")),
            "estado_operativo": "",
            "fecha_inicio": f.get("start_date"),
            "fecha_asignacion": f.get("assignment_date"),
            "fecha_solucion": f.get("resolution_date"),
            "fecha_cierre": f.get("close_date"),
            "fecha_fin": f.get("end_date"),
            "fecha_real_solucion": None,
            "last_update_itop": f.get("last_update"),
        })

    return filas
