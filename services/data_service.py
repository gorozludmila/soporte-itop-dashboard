from pathlib import Path
from datetime import timedelta
import os
import re
import unicodedata
import pandas as pd
from services.database import obtener_tickets

# ARCHIVOS

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DATA_DIR = BASE_DIR / "data"
EXTERNAL_DATA_DIR = Path( os.environ.get( "ITOP_DATA_DIR", "/home/usuario/Documentos/PROYECTO" ))


def _data_dir():

    candidatos = [EXTERNAL_DATA_DIR,   PROJECT_DATA_DIR]
    for carpeta in candidatos:
        if (   carpeta /"Jefe_de_Sectoriales_con_sus_Usuarios.csv").exists():

            return carpeta

    return PROJECT_DATA_DIR


def rutas_archivos():
    carpeta = _data_dir()
    return ( carpeta / "Incidente Exportar.csv", carpeta / "Requerimiento Exportar.csv", carpeta / "Jefe_de_Sectoriales_con_sus_Usuarios.csv" )

# MINISTERIOS
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

    # Organismos cuyo código no identifica de forma inequívoca un ministerio.
    "API": "Organismos descentralizados",
    "IAPOS": "Organismos descentralizados",
    "LIF": "Organismos descentralizados",
    "DPVyU": "Organismos descentralizados",
    "DPV": "Organismos descentralizados",
    "LOTERIA": "Organismos descentralizados",
    "TC": "Organismos descentralizados",
    "FE": "Organismos descentralizados",
    "ME": "Organismos descentralizados",
    "OD": "Otros organismos",
}

# UTILIDADES
def leer_csv(ruta):
    return pd.read_csv(ruta, encoding="utf-8-sig", sep=None,engine="python")

def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def normalizar_texto(valor):
    valor = limpiar_texto(valor).lower()
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(c for c in valor if not unicodedata.combining(c))
    valor = re.sub(r"[^a-z0-9 ]", " ", valor)
    valor = re.sub(r"\s+", " ", valor)
    return valor.strip()


def clave_nombre(valor):
    # También iguala 'Pérez Juan' con 'Juan Pérez'.
    return " ".join(sorted(normalizar_texto(valor).split()))


def obtener_codigo_organizacion(organizacion):
    organizacion = limpiar_texto(organizacion)
    if not organizacion:
        return ""
    return organizacion.split("#", 1)[0].strip()


def obtener_ministerio(organizacion):
    codigo = obtener_codigo_organizacion(organizacion)
    if not codigo:
        return "Sin Ministerio"
    return MINISTERIOS.get(codigo, f"Otros ({codigo})")


def convertir_fecha(serie):
    return pd.to_datetime(serie, dayfirst=True, errors="coerce")


def _texto_columna(df, campo):
    df[campo] = df[campo].fillna("").astype(str).str.strip()


# ============================================================
# ADMINISTRADORES LOCALES
# ============================================================

def cargar_administradores():
    _, _, archivo = rutas_archivos()
    df = leer_csv(archivo)
    admins = []

    for _, fila in df.iterrows():
        organismo = limpiar_texto(fila.get("ORGANISMO"))
        sectorial = limpiar_texto(fila.get("SECTORIAL"))
        titular = limpiar_texto(fila.get("TITULAR"))
        usuarios = limpiar_texto(fila.get("USUARIOS TIMBO - ADM LOCAL"))

        if not usuarios:
            continue

        for nombre in usuarios.split(";"):
            nombre = nombre.strip()
            if not nombre:
                continue
            admins.append({
                "organismo_admin": organismo,
                "sectorial": sectorial,
                "titular": titular,
                "nombre": nombre,
                "nombre_key": clave_nombre(nombre),
                "ministerio_admin": obtener_ministerio(organismo),
            })

    if not admins:
        return pd.DataFrame(columns=[ "organismo_admin", "sectorial", "titular", "nombre", "nombre_key", "ministerio_admin" ])

    return pd.DataFrame(admins).drop_duplicates(
        subset=["nombre_key", "organismo_admin"]
    )

# INCIDENTES / REQUERIMIENTOS
def _dataframe_tickets_vacio():
    return pd.DataFrame(columns=[
        "referencia",
        "tipo",
        "asunto",
        "organizacion",
        "reportado_por",
        "analista",
        "servicio",
        "estado",
        "estado_operativo",
        "fecha_inicio",
        "fecha_asignacion",
        "fecha_solucion",
        "fecha_cierre",
        "fecha_fin",
        "fecha_real_solucion",
    ])


def _cargar_tickets_desde_bd(tipo=None):
    datos = obtener_tickets(tipo=tipo)
    df = pd.DataFrame(datos)

    if df.empty:
        return preparar_tickets(_dataframe_tickets_vacio())

    columnas_texto = [
        "referencia",
        "tipo",
        "asunto",
        "organizacion",
        "reportado_por",
        "analista",
        "servicio",
        "estado",
        "estado_operativo",
    ]

    for campo in columnas_texto:
        if campo not in df.columns:
            df[campo] = ""

    columnas_fecha = [
        "fecha_inicio",
        "fecha_asignacion",
        "fecha_solucion",
        "fecha_cierre",
        "fecha_fin",
        "fecha_real_solucion",
    ]

    for campo in columnas_fecha:
        if campo not in df.columns:
            df[campo] = pd.NaT
        else:
            df[campo] = convertir_fecha(df[campo])

    return preparar_tickets(df)


def cargar_incidentes():
    return _cargar_tickets_desde_bd("Incidente")


def cargar_requerimientos():
    return _cargar_tickets_desde_bd("Requerimiento")


def preparar_tickets(df):
    df = df.copy()
    df = df.drop_duplicates(subset=["referencia"], keep="last")

    for campo in [
        "referencia",
        "asunto",
        "organizacion",
        "reportado_por",
        "analista",
        "servicio",
        "estado",
        "estado_operativo",
    ]:
        _texto_columna(df, campo)

    df["ministerio"] = df["organizacion"].apply(obtener_ministerio)
    df["organismo"] = df["organizacion"]
    df["reportado_key"] = df["reportado_por"].apply(clave_nombre)

    estado_normalizado = df["estado"].apply(normalizar_texto)
    df["estado_grupo"] = "Abierto"
    df.loc[estado_normalizado == "cerrado", "estado_grupo"] = "Cerrado"
    df.loc[
        estado_normalizado.isin(["solucionado", "resuelto"]),
        "estado_grupo"
    ] = "Resuelto"

    return df


def cargar_tickets():
    tickets = _cargar_tickets_desde_bd()
    return identificar_administradores(tickets)


def identificar_administradores(tickets):
    admins = cargar_administradores()
    keys = set(admins["nombre_key"].tolist()) if not admins.empty else set()

    tickets = tickets.copy()
    tickets["es_admin_local"] = tickets["reportado_key"].isin(keys)
    tickets["admin_local"] = tickets["reportado_por"].where(
        tickets["es_admin_local"], ""
    )
    return tickets

# FILTROS
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
    persona=None,
):
    df = tickets.copy()

    if desde:
        fecha = pd.to_datetime(desde, errors="coerce")
        if not pd.isna(fecha):
            df = df[df["fecha_inicio"] >= fecha]

    if hasta:
        fecha = pd.to_datetime(hasta, errors="coerce")
        if not pd.isna(fecha):
            df = df[df["fecha_inicio"] < fecha + timedelta(days=1)]

    if ministerio:
        df = df[df["ministerio"] == ministerio]

    if organismo:
        df = df[df["organismo"] == organismo]

    if tipo:
        df = df[df["tipo"] == tipo]

    if estado:
        if estado == "__abiertos__":
            df = df[df["estado_grupo"] == "Abierto"]
        elif estado == "__finalizados__":
            df = df[df["estado_grupo"].isin(["Cerrado", "Resuelto"])]
        else:
            df = df[df["estado"] == estado]

    if servicio:
        df = df[df["servicio"] == servicio]

    if persona:
        columnas = {
            "reportado": "reportado_por",
            "admin": "admin_local",
            "analista": "analista",
        }
        columna = columnas.get(persona_tipo)
        if columna:
            df = df[df[columna] == persona]

    return df


# ============================================================
# RESÚMENES
# ============================================================

def resumen_numerico(df):
    total = int(len(df))
    incidentes = int((df["tipo"] == "Incidente").sum())
    requerimientos = int((df["tipo"] == "Requerimiento").sum())
    cerrados = int((df["estado_grupo"] == "Cerrado").sum())
    resueltos = int((df["estado_grupo"] == "Resuelto").sum())
    abiertos = int((df["estado_grupo"] == "Abierto").sum())
    finalizados = cerrados + resueltos

    return {
        "total": total,
        "incidentes": incidentes,
        "requerimientos": requerimientos,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "resueltos": resueltos,
        "finalizados": finalizados,
        "porcentaje_resolucion": round(finalizados * 100 / total, 1) if total else 0,
    }


def contar_por(df, campo, limite=None):
    if campo not in df.columns:
        return []
    serie = df[campo].fillna("").astype(str).str.strip()
    serie = serie[serie != ""]
    conteo = serie.value_counts()
    if limite:
        conteo = conteo.head(limite)
    return [
        {"nombre": str(nombre), "cantidad": int(cantidad)}
        for nombre, cantidad in conteo.items()
    ]


def resumen_administradores(df, limite=None):
    admins = df[df["es_admin_local"]].copy()
    if admins.empty:
        return []

    agrupado = (
        admins.groupby(["admin_local", "ministerio", "organismo", "tipo"])
        .size()
        .reset_index(name="cantidad")
    )

    salida = {}
    for _, fila in agrupado.iterrows():
        clave = (fila["admin_local"], fila["ministerio"], fila["organismo"])
        if clave not in salida:
            salida[clave] = {
                "nombre": fila["admin_local"],
                "ministerio": fila["ministerio"],
                "organismo": fila["organismo"],
                "incidentes": 0,
                "requerimientos": 0,
                "cantidad": 0,
            }
        if fila["tipo"] == "Incidente":
            salida[clave]["incidentes"] += int(fila["cantidad"])
        else:
            salida[clave]["requerimientos"] += int(fila["cantidad"])
        salida[clave]["cantidad"] += int(fila["cantidad"])

    filas = sorted(salida.values(), key=lambda x: x["cantidad"], reverse=True)
    return filas[:limite] if limite else filas


# ============================================================
# EVOLUCIÓN Y TIEMPOS
# ============================================================

def _etiqueta_periodo(serie, agrupacion):
    if agrupacion == "semana":
        lunes = serie - pd.to_timedelta(serie.dt.weekday, unit="D")
        return lunes.dt.strftime("%Y-%m-%d")
    if agrupacion == "anio":
        return serie.dt.strftime("%Y")
    return serie.dt.strftime("%Y-%m")


def evolucion(df, agrupacion="mes", desde=None, hasta=None):
    if agrupacion not in ["semana", "mes", "anio"]:
        agrupacion = "mes"

    recibidos = df[df["fecha_inicio"].notna()].copy()
    recibidos["periodo"] = _etiqueta_periodo(recibidos["fecha_inicio"], agrupacion)
    serie_recibidos = recibidos.groupby("periodo").size()

    terminados = df.copy()
    terminados["fecha_final"] = (
        terminados["fecha_real_solucion"]
        .fillna(terminados["fecha_solucion"])
        .fillna(terminados["fecha_cierre"])
        .fillna(terminados["fecha_fin"])
    )
    terminados = terminados[terminados["estado_grupo"].isin(["Cerrado", "Resuelto"]) & terminados["fecha_final"].notna()].copy()
    
    terminados["periodo"] = _etiqueta_periodo(terminados["fecha_final"], agrupacion)
    serie_finalizados = terminados.groupby("periodo").size()
    if desde:
            fecha_desde = pd.to_datetime(desde, errors="coerce")
            if not pd.isna(fecha_desde):
                terminados = terminados[terminados["fecha_inicio"] >= fecha_desde]
    if hasta:
        fecha_hasta = pd.to_datetime(hasta, errors="coerce")
        if not pd.isna(fecha_hasta):
            terminados = terminados[terminados["fecha_inicio"] < fecha_hasta + timedelta(days=1)]
            
    periodos = sorted(set(serie_recibidos.index) | set(serie_finalizados.index))
    return [
        {
            "periodo": periodo,
            "recibidos": int(serie_recibidos.get(periodo, 0)),
            "cerrados": int(serie_finalizados.get(periodo, 0)),
        }
        for periodo in periodos
    ]


def tiempo_promedio_horas(df):
    temp = df.copy()
    temp["fecha_resolucion_final"] = (
        temp["fecha_real_solucion"]
        .fillna(temp["fecha_solucion"])
        .fillna(temp["fecha_cierre"])
        .fillna(temp["fecha_fin"])
    )
    temp = temp[
        temp["fecha_inicio"].notna()
        & temp["fecha_resolucion_final"].notna()
    ]
    if temp.empty:
        return 0
    horas = (
        temp["fecha_resolucion_final"] - temp["fecha_inicio"]
    ).dt.total_seconds() / 3600
    horas = horas[(horas >= 0) & horas.notna()]
    return round(float(horas.mean()), 1) if not horas.empty else 0


# ============================================================
# OPCIONES DE FILTROS
# ============================================================

def opciones_filtros():
    tickets = cargar_tickets()

    def valores(campo):
        serie = tickets[campo].dropna().astype(str).str.strip()
        return sorted(serie[serie != ""].unique().tolist())

    organismos_por_ministerio = {}
    for ministerio, grupo in tickets.groupby("ministerio"):
        serie = grupo["organismo"].dropna().astype(str).str.strip()
        organismos_por_ministerio[ministerio] = sorted(
            serie[serie != ""].unique().tolist()
        )

    admins = tickets[tickets["es_admin_local"]]

    return {
        "ministerios": valores("ministerio"),
        "organismos": valores("organismo"),
        "organismos_por_ministerio": organismos_por_ministerio,
        "estados": valores("estado"),
        "servicios": valores("servicio"),
        "personas": {
            "reportado": valores("reportado_por"),
            "analista": valores("analista"),
            "admin": sorted(admins["admin_local"].dropna().astype(str).unique().tolist()),
            "creador": [],
        },
    }


# ============================================================
# MINISTERIOS / ORGANISMOS
# ============================================================

def resumen_ministerios(df):
    salida = []
    for ministerio, grupo in df.groupby("ministerio"):
        r = resumen_numerico(grupo)
        salida.append({"ministerio": ministerio, **r})
    return sorted(salida, key=lambda x: x["total"], reverse=True)


def detalle_ministerio(df, ministerio):
    resumen = resumen_numerico(df)

    organismos = []
    for organismo, grupo in df.groupby("organismo"):
        r = resumen_numerico(grupo)
        organismos.append({
            "organismo": organismo,
            "incidentes": r["incidentes"],
            "requerimientos": r["requerimientos"],
            "abiertos": r["abiertos"],
            "cerrados": r["cerrados"],
            "resueltos": r["resueltos"],
            "total": r["total"],
        })
    organismos.sort(key=lambda x: x["total"], reverse=True)

    admins = resumen_administradores(df)
    admins_inc = [
        {"nombre": x["nombre"], "organismo": x["organismo"], "cantidad": x["incidentes"]}
        for x in admins if x["incidentes"] > 0
    ]
    admins_req = [
        {"nombre": x["nombre"], "organismo": x["organismo"], "cantidad": x["requerimientos"]}
        for x in admins if x["requerimientos"] > 0
    ]

    return {
        "ministerio": ministerio,
        "resumen": resumen,
        "organismos": organismos,
        "admins_incidentes": admins_inc,
        "admins_requerimientos": admins_req,
    }


def detalle_organismo(df, organismo):
    resumen = resumen_numerico(df)
    admins = resumen_administradores(df)
    return {
        "organismo": organismo,
        "resumen": resumen,
        "admins_incidentes": [
            {"nombre": x["nombre"], "cantidad": x["incidentes"]}
            for x in admins if x["incidentes"] > 0
        ],
        "admins_requerimientos": [
            {"nombre": x["nombre"], "cantidad": x["requerimientos"]}
            for x in admins if x["requerimientos"] > 0
        ],
    }
