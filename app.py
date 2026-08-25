from flask import Flask, render_template, jsonify, request
from exportacionitop import ejecutar
from datetime import datetime, timedelta
from services.data_service import (
    cargar_tickets,
    aplicar_filtros,
    resumen_numerico,
    contar_por,
    opciones_filtros,
    evolucion,
    tiempo_promedio_horas,
    resumen_ministerios,
    detalle_ministerio,
    detalle_organismo,
)


app = Flask(__name__)


# ============================================================
# PÁGINAS
# ============================================================

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/incidentes")
def incidentes():
    return render_template("incidentes.html")


@app.route("/requerimientos")
def requerimientos():
    return render_template("requerimientos.html")


@app.route("/ministerios")
def ministerios():
    return render_template("ministerios.html")


@app.route("/administradores")
def administradores():
    return render_template("administradores.html")


# ============================================================
# FILTROS RECIBIDOS DESDE EL FRONTEND
# ============================================================

def obtener_filtros():

    return {
        "desde": request.args.get("desde"),
        "hasta": request.args.get("hasta"),
        "ministerio": request.args.get("ministerio"),
        "organismo": request.args.get("organismo"),
        "tipo": request.args.get("tipo"),
        "estado": request.args.get("estado"),
        "servicio": request.args.get("servicio"),
        "persona_tipo": request.args.get("persona_tipo"),
        "persona": request.args.get("persona"),
    }


# ============================================================
# FUNCIÓN AUXILIAR
#
# En este proyecto:
#
# reportado_por = Administrador Local
#
# Agrupamos por:
# Administrador + Ministerio + Organismo
# ============================================================

def resumen_por_administrador(tickets):

    if tickets.empty:
        return []


    admins = (

        tickets[
            tickets["reportado_por"]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        ]

        .groupby( [  "reportado_por", "ministerio", "organismo" ],   dropna=False )
        .agg(  incidentes=("tipo",  lambda x:  int(       (x == "Incidente").sum() )   ),
        requerimientos=(   "tipo",  lambda x:   int(      (x == "Requerimiento").sum()) ), cantidad=( "referencia", "count" ))
        .reset_index()
        .sort_values("cantidad",   ascending=False   ) )


    return [ {
            "nombre":  fila["reportado_por"],
            "ministerio": fila["ministerio"],
            "organismo":  fila["organismo"],
            "incidentes":  int(fila["incidentes"]),
            "requerimientos": int(fila["requerimientos"]),
            "cantidad": int(fila["cantidad"])
        }

        for _, fila
        in admins.iterrows()

    ]


# ============================================================
# API FILTROS
# ============================================================

@app.route("/api/filtros")
def api_filtros():

    try:
        return jsonify({ "ok": True,   "data": opciones_filtros()  })

    except Exception as error:
        return jsonify({ "ok": False, "error": str(error) }), 500


# ============================================================
# API DASHBOARD GENERAL
# ============================================================

@app.route("/api/resumen")
def api_resumen():

    try:
        tickets = aplicar_filtros( cargar_tickets(), **obtener_filtros()  )
        filtros = obtener_filtros()
        resumen = resumen_numerico(  tickets)

        resumen["ministerios"] = contar_por(tickets, "ministerio", 12 )
        resumen["organismos"] = contar_por( tickets,  "organismo", 12 )
        resumen["servicios"] = contar_por( tickets, "servicio", 12 )
        resumen["estados"] = contar_por( tickets,"estado"  )
        resumen["evolucion"] = evolucion(
    tickets,
    request.args.get("agrupacion", "mes"),
    filtros["desde"],
    filtros["hasta"]
)
        resumen["tiempo_promedio_horas"] = ( tiempo_promedio_horas( tickets  ) )


        # ----------------------------------------
        # TODOS LOS REPORTANTES SON ADM. LOCALES
        #
        # Lo dejamos temporalmente para no romper
        # dashboard.js si todavía usa d.origen.
        # Después podemos sacar ese gráfico.
        # ----------------------------------------

        resumen["origen"] = {            "administradores":  int(len(tickets)),  "otros":       0 }


        return jsonify({
            "ok": True,
            "data": resumen
        })


    except Exception as error:

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500


# ============================================================
# API INCIDENTES / REQUERIMIENTOS
# ============================================================

@app.route("/api/tickets")
def api_tickets():

    try:

        filtros = obtener_filtros()


        # Incidentes manda:
        # solo_tipo=Incidente
        #
        # Requerimientos manda:
        # solo_tipo=Requerimiento

        solo_tipo = request.args.get(
            "solo_tipo"
        )


        if solo_tipo:

            filtros["tipo"] = solo_tipo


        tickets = aplicar_filtros(cargar_tickets(), **filtros)
        resumen = resumen_numerico(tickets        )
        resumen["evolucion"] = evolucion( tickets, request.args.get("agrupacion", "mes"),  filtros["desde"], filtros["hasta"])
        resumen["por_ministerio"] = contar_por(  tickets,  "ministerio", 15 )
        resumen["por_organismo"] = contar_por(tickets,   "organismo",  15)
        resumen["por_servicio"] = contar_por(  tickets, "servicio",  15 )
        resumen["por_estado"] = contar_por( tickets, "estado"  )
        administradores = resumen_por_administrador( tickets)
        resumen["por_admin"] = administradores

        resumen["por_reportante"] = [

            {
                "nombre":
                    admin["nombre"],

                "cantidad":
                    admin["cantidad"]
            }

            for admin
            in administradores

        ]


        return jsonify({
            "ok": True,
            "data": resumen
        })


    except Exception as error:

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500


# ============================================================
# API MINISTERIOS
# ============================================================

@app.route("/api/ministerios")
def api_ministerios():

    try:

        tickets = aplicar_filtros(
            cargar_tickets(),
            **obtener_filtros()
        )


        return jsonify({

            "ok": True,

            "data": {

                "ministerios":
                    resumen_ministerios(
                        tickets
                    )
            }
        })


    except Exception as error:

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500


# ============================================================
# DETALLE DE MINISTERIO
# ============================================================

@app.route("/api/ministerios/detalle")
def api_ministerio_detalle():

    try:

        ministerio = request.args.get(
            "ministerio",
            ""
        ).strip()


        if not ministerio:

            return jsonify({

                "ok": False,

                "error":
                    "Debe indicar un ministerio."

            }), 400


        filtros = obtener_filtros()

        filtros["ministerio"] = (
            ministerio
        )


        tickets = aplicar_filtros(
            cargar_tickets(),
            **filtros
        )


        # Datos generales del Ministerio
        detalle = detalle_ministerio(
            tickets,
            ministerio
        )


        # ----------------------------------------
        # ADMINISTRADORES DEL MINISTERIO
        # ----------------------------------------

        administradores = (
            resumen_por_administrador(
                tickets
            )
        )


        # ----------------------------------------
        # INCIDENTES POR ADMINISTRADOR
        # ----------------------------------------

        detalle[
            "admins_incidentes"
        ] = [

            {
                "nombre":
                    admin["nombre"],

                "organismo":
                    admin["organismo"],

                "cantidad":
                    admin["incidentes"]
            }

            for admin
            in administradores

            if admin["incidentes"] > 0

        ]


        # ----------------------------------------
        # REQUERIMIENTOS POR ADMINISTRADOR
        # ----------------------------------------

        detalle[
            "admins_requerimientos"
        ] = [

            {
                "nombre":
                    admin["nombre"],

                "organismo":
                    admin["organismo"],

                "cantidad":
                    admin[
                        "requerimientos"
                    ]
            }

            for admin
            in administradores

            if (
                admin[
                    "requerimientos"
                ]
                > 0
            )

        ]


        return jsonify({
            "ok": True,
            "data": detalle
        })


    except Exception as error:

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500


# ============================================================
# DETALLE DE ORGANISMO
# ============================================================

@app.route("/api/organismos/detalle")
def api_organismo_detalle():

    try:

        organismo = request.args.get(
            "organismo",
            ""
        ).strip()


        if not organismo:

            return jsonify({

                "ok": False,

                "error":
                    "Debe indicar un organismo."

            }), 400


        filtros = obtener_filtros()

        filtros["organismo"] = (
            organismo
        )


        tickets = aplicar_filtros(
            cargar_tickets(),
            **filtros
        )


        detalle = detalle_organismo(
            tickets,
            organismo
        )


        # Administradores de este organismo

        detalle[
            "administradores"
        ] = resumen_por_administrador(
            tickets
        )


        return jsonify({
            "ok": True,
            "data": detalle
        })


    except Exception as error:

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500


# ============================================================
# API ADMINISTRADORES LOCALES
# ============================================================

@app.route("/api/administradores")
def api_administradores():

    try:

        tickets = aplicar_filtros(
            cargar_tickets(),
            **obtener_filtros()
        )


        filas = resumen_por_administrador(
            tickets
        )


        return jsonify({

            "ok": True,

            "data": {

                "total_administradores":
                    len(filas),


                "total_incidentes":
                    sum(
                        x["incidentes"]
                        for x in filas
                    ),


                "total_requerimientos":
                    sum(
                        x["requerimientos"]
                        for x in filas
                    ),


                "total_tickets":
                    sum(
                        x["cantidad"]
                        for x in filas
                    ),


                "administradores":
                    filas
            }
        })


    except Exception as error:

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500

@app.route("/actualizar-datos", methods=["POST"])
def actualizar_datos():
    try:
        ejecutar()

        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return {
            "ok": True,
            "mensaje": "Datos actualizados correctamente",
            "fecha": ahora
        }

    except Exception as error:

        print("ERROR AL ACTUALIZAR DATOS:")
        print(error)

        return {
            "ok": False,
            "mensaje": str(error)
        }, 500
# ============================================================
# SERVIDOR
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=4000,
        debug=True
    )