from pathlib import Path
from datetime import datetime, timedelta
import re
import unicodedata

import pandas as pd


# ============================================================
# ARCHIVOS
# ============================================================

DATA_DIR = Path("/home/usuario/Documentos/PROYECTO")

INCIDENTES_FILE = DATA_DIR / "Incidente Exportar.csv"
REQUERIMIENTOS_FILE = DATA_DIR / "Requerimiento Exportar.csv"
ADMINISTRADORES_FILE = DATA_DIR / "Jefe_de_Sectoriales_con_sus_Usuarios.csv"


# ============================================================
# MINISTERIOS
# ============================================================

MINISTERIOS = {
    "MGeIP": "Ministerio de Gobierno e Innovación Pública",
    "MTEySS": "Ministerio de Trabajo, Empleo y Seguridad Social",
    "MS": "Ministerio de Salud",
    "MEC": "Ministerio de Economía",
    "MED": "Ministerio de Educación",
    "MDP": "Ministerio de Desarrollo Productivo",
    "MIyDH": "Ministerio de Igualdad y Desarrollo Humano",
    "MOP": "Ministerio de Obras Públicas",
    "MC": "Ministerio de Cultura",
    "MAyCC": "Ministerio de Ambiente y Cambio Climático",
    "MJyS": "Ministerio de Justicia y Seguridad",

    # Organismos descentralizados
    "API": "Organismos Descentralizados",
    "IAPOS": "Organismos Descentralizados",
    "LIF": "Organismos Descentralizados",
    "DPVyU": "Organismos Descentralizados",
    "DPV": "Organismos Descentralizados",
    "LOTERIA": "Organismos Descentralizados",
    "TC": "Organismos Descentralizados",
    "FE": "Organismos Descentralizados",
    "ME": "Organismos Descentralizados",
    "OD": "Otros Organismos"
}


# ============================================================
# UTILIDADES
# ============================================================

def leer_csv(ruta):
    return pd.read_csv(
        ruta,
        encoding="utf-8-sig",
        sep=None,
        engine="python"
    )


def limpiar_texto(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def normalizar_nombre(valor):
    """
    Convierte:
    'María Pérez'
    'MARIA PEREZ'
    'María   Pérez'

    en una forma comparable.
    """

    valor = limpiar_texto(valor).lower()

    valor = unicodedata.normalize("NFKD", valor)

    valor = "".join(
        c for c in valor
        if not unicodedata.combining(c)
    )

    valor = re.sub(r"[^a-z0-9 ]", " ", valor)
    valor = re.sub(r"\s+", " ", valor)

    return valor.strip()


def obtener_codigo_organizacion(organizacion):
    organizacion = limpiar_texto(organizacion)

    if not organizacion:
        return ""

    return organizacion.split("#")[0].strip()


def obtener_ministerio(organizacion):
    codigo = obtener_codigo_organizacion(organizacion)

    return MINISTERIOS.get(
        codigo,
        codigo if codigo else "Sin Ministerio"
    )


def convertir_fecha(serie):
    return pd.to_datetime(
        serie,
        dayfirst=True,
        errors="coerce"
    )


# ============================================================
# ADMINISTRADORES LOCALES
# ============================================================

def cargar_administradores():
    df = leer_csv(ADMINISTRADORES_FILE)

    admins = []

    for _, fila in df.iterrows():

        organismo = limpiar_texto(
            fila.get("ORGANISMO")
        )

        sectorial = limpiar_texto(
            fila.get("SECTORIAL")
        )

        titular = limpiar_texto(
            fila.get("TITULAR")
        )

        usuarios = limpiar_texto(
            fila.get("USUARIOS TIMBO - ADM LOCAL")
        )

        if not usuarios:
            continue

        nombres = usuarios.split(";")

        for nombre in nombres:

            nombre = nombre.strip()

            if not nombre:
                continue

            admins.append({
                "organismo": organismo,
                "sectorial": sectorial,
                "titular": titular,
                "nombre": nombre,
                "nombre_normalizado": normalizar_nombre(nombre),
                "ministerio": obtener_ministerio(organismo)
            })

    return pd.DataFrame(admins)


# ============================================================
# INCIDENTES
# ============================================================

def cargar_incidentes():

    df = leer_csv(INCIDENTES_FILE)

    tickets = pd.DataFrame({
        "referencia":
            df["Incident.Ref"],

        "tipo":
            "Incidente",

        "asunto":
            df["Incident.Asunto"],

        "organizacion":
            df["Incident.Organización->Nombre común"],

        "reportado_por":
            df["Incident.Reportado por->Nombre común"],

        "analista":
            df["Incident.Analista->Nombre común"],

        "servicio":
            df["Service.Nombre"],

        "estado":
            df["Incident.Estatus"],

        "estado_operativo":
            df["Incident.Estatus Operativo"],

        "fecha_inicio":
            convertir_fecha(
                df["Incident.Fecha de Inicio"]
            ),

        "fecha_asignacion":
            convertir_fecha(
                df["Incident.Fecha de Asignación"]
            ),

        "fecha_solucion":
            convertir_fecha(
                df["Incident.Fecha de Solución"]
            ),

        "fecha_cierre":
            convertir_fecha(
                df["Incident.Fecha de Cierre"]
            ),

        "fecha_fin":
            convertir_fecha(
                df["Incident.Fecha de Fin"]
            ),

        "fecha_real_solucion":
            convertir_fecha(
                df["Incident.Fecha Real de Solución"]
            )
    })

    return preparar_tickets(tickets)


# ============================================================
# REQUERIMIENTOS
# ============================================================

def cargar_requerimientos():

    df = leer_csv(REQUERIMIENTOS_FILE)

    tickets = pd.DataFrame({
        "referencia":
            df["UserRequest.Ref"],

        "tipo":
            "Requerimiento",

        "asunto":
            df["UserRequest.Asunto"],

        "organizacion":
            df["UserRequest.Organización->Nombre común"],

        "reportado_por":
            df["UserRequest.Reportado por->Nombre común"],

        "analista":
            df["UserRequest.Analista->Nombre común"],

        "servicio":
            df["Service.Nombre"],

        "estado":
            df["UserRequest.Estatus"],

        "estado_operativo":
            df["UserRequest.Estatus Operativo"],

        "fecha_inicio":
            convertir_fecha(
                df["UserRequest.Fecha de Inicio"]
            ),

        "fecha_asignacion":
            convertir_fecha(
                df["UserRequest.Fecha de Asignación"]
            ),

        "fecha_solucion":
            convertir_fecha(
                df["UserRequest.Fecha de Solución"]
            ),

        "fecha_cierre":
            convertir_fecha(
                df["UserRequest.Fecha de Cierre"]
            ),

        "fecha_fin":
            convertir_fecha(
                df["UserRequest.Fecha de Fin"]
            ),

        "fecha_real_solucion":
            convertir_fecha(
                df["UserRequest.Fecha Real de Solución"]
            )
    })

    return preparar_tickets(tickets)


# ============================================================
# PREPARAR TICKETS
# ============================================================

def preparar_tickets(df):

    df = df.copy()

    df = df.drop_duplicates(
        subset=["referencia"],
        keep="last"
    )

    df["ministerio"] = df["organizacion"].apply(
        obtener_ministerio
    )

    df["organismo"] = df["organizacion"]

    df["reportado_normalizado"] = (
        df["reportado_por"]
        .fillna("")
        .apply(normalizar_nombre)
    )

    df["estado_grupo"] = df.apply(
        clasificar_estado,
        axis=1
    )

    return df


# ============================================================
# ESTADOS
# ============================================================

def clasificar_estado(fila):

    estado = normalizar_nombre(
        fila.get("estado", "")
    )

    cerrado = [
        "cerrado",
        "solucionado",
        "resuelto",
        "completado"
    ]

    if any(x in estado for x in cerrado):
        return "Cerrado"

    return "Abierto"


# ============================================================
# CARGAR TODO
# ============================================================

def cargar_tickets():

    incidentes = cargar_incidentes()
    requerimientos = cargar_requerimientos()

    tickets = pd.concat(
        [incidentes, requerimientos],
        ignore_index=True
    )

    tickets = identificar_administradores(tickets)

    return tickets


# ============================================================
# IDENTIFICAR ADMIN LOCAL
# ============================================================

def identificar_administradores(tickets):

    admins = cargar_administradores()

    nombres_admin = set(
        admins["nombre_normalizado"]
    )

    tickets = tickets.copy()

    tickets["es_admin_local"] = (
        tickets["reportado_normalizado"]
        .isin(nombres_admin)
    )

    tickets["admin_local"] = tickets.apply(
        lambda fila:
            fila["reportado_por"]
            if fila["es_admin_local"]
            else "",
        axis=1
    )

    return tickets


# ============================================================
# FILTROS
# ============================================================

def aplicar_filtros(
    tickets,
    desde=None,
    hasta=None,
    ministerio=None,
    organismo=None,
    tipo=None,
    estado=None,
    servicio=None,
    persona_tipo=None,
    persona=None
):

    df = tickets.copy()

    if desde:
        fecha = pd.to_datetime(desde)

        df = df[
            df["fecha_inicio"] >= fecha
        ]

    if hasta:
        fecha = (
            pd.to_datetime(hasta)
            + timedelta(days=1)
        )

        df = df[
            df["fecha_inicio"] < fecha
        ]

    if ministerio:
        df = df[
            df["ministerio"] == ministerio
        ]

    if organismo:
        df = df[
            df["organismo"] == organismo
        ]

    if tipo:
        df = df[
            df["tipo"] == tipo
        ]

    if estado:

        if estado in ["Abierto", "Cerrado"]:

            df = df[
                df["estado_grupo"] == estado
            ]

        else:

            df = df[
                df["estado"] == estado
            ]

    if servicio:
        df = df[
            df["servicio"] == servicio
        ]

    if persona:

        columnas = {
            "reportado": "reportado_por",
            "admin": "admin_local",
            "analista": "analista"
        }

        columna = columnas.get(
            persona_tipo,
            "reportado_por"
        )

        if columna in df.columns:

            df = df[
                df[columna] == persona
            ]

    return df


# ============================================================
# RESUMEN
# ============================================================

def resumen_numerico(df):

    total = len(df)

    incidentes = len(
        df[df["tipo"] == "Incidente"]
    )

    requerimientos = len(
        df[df["tipo"] == "Requerimiento"]
    )

    cerrados = len(
        df[df["estado_grupo"] == "Cerrado"]
    )

    abiertos = total - cerrados

    porcentaje = (
        round(cerrados / total * 100, 1)
        if total
        else 0
    )

    return {
        "total": total,
        "incidentes": incidentes,
        "requerimientos": requerimientos,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "porcentaje_resolucion": porcentaje
    }


# ============================================================
# CONTAR POR CAMPO
# ============================================================

def contar_por(df, campo, limite=None):

    if campo not in df.columns:
        return []

    datos = (
        df[campo]
        .fillna("Sin dato")
        .replace("", "Sin dato")
        .value_counts()
    )

    if limite:
        datos = datos.head(limite)

    return [
        {
            "nombre": str(nombre),
            "cantidad": int(cantidad)
        }
        for nombre, cantidad in datos.items()
    ]


# ============================================================
# EVOLUCIÓN TEMPORAL
# ============================================================

def evolucion(df):

    temp = df[
        df["fecha_inicio"].notna()
    ].copy()

    if temp.empty:
        return []

    temp["periodo"] = (
        temp["fecha_inicio"]
        .dt.to_period("M")
        .astype(str)
    )

    recibidos = (
        temp
        .groupby("periodo")
        .size()
    )

    cerrados = (
        temp[
            temp["estado_grupo"] == "Cerrado"
        ]
        .groupby("periodo")
        .size()
    )

    periodos = sorted(
        set(recibidos.index)
        | set(cerrados.index)
    )

    return [
        {
            "periodo": periodo,
            "recibidos": int(
                recibidos.get(periodo, 0)
            ),
            "cerrados": int(
                cerrados.get(periodo, 0)
            )
        }
        for periodo in periodos
    ]


# ============================================================
# TIEMPO PROMEDIO
# ============================================================

def tiempo_promedio_horas(df):

    temp = df.copy()

    temp["fecha_resolucion_final"] = (
        temp["fecha_real_solucion"]
        .fillna(temp["fecha_solucion"])
        .fillna(temp["fecha_cierre"])
    )

    temp = temp[
        temp["fecha_inicio"].notna()
        & temp["fecha_resolucion_final"].notna()
    ]

    if temp.empty:
        return 0

    horas = (
        temp["fecha_resolucion_final"]
        - temp["fecha_inicio"]
    ).dt.total_seconds() / 3600

    horas = horas[
        horas >= 0
    ]

    if horas.empty:
        return 0

    return round(
        horas.mean(),
        1
    )


# ============================================================
# OPCIONES DE FILTROS
# ============================================================

def opciones_filtros():

    tickets = cargar_tickets()

    admins = cargar_administradores()

    def valores(campo):
        return sorted(
            tickets[campo]
            .dropna()
            .astype(str)
            .loc[lambda x: x.str.strip() != ""]
            .unique()
            .tolist()
        )

    return {
        "ministerios":
            valores("ministerio"),

        "organismos":
            valores("organismo"),

        "estados":
            valores("estado"),

        "servicios":
            valores("servicio"),

        "personas": {

            "reportado":
                valores("reportado_por"),

            "analista":
                valores("analista"),

            "admin":
                sorted(
                    admins["nombre"]
                    .dropna()
                    .unique()
                    .tolist()
                )
        }
    }