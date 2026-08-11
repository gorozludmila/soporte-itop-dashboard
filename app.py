from flask import Flask, render_template, jsonify

from services.data_service import cargar_tickets

app = Flask(__name__)


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


@app.route("/api/resumen")
def api_resumen():

    tickets = cargar_tickets()

    total = len(tickets)

    incidentes = len(
        tickets[tickets["tipo"] == "Incidente"]
    )

    requerimientos = len(
        tickets[tickets["tipo"] == "Requerimiento"]
    )

    estados_cerrados = [
        "Cerrado",
        "Resuelto",
        "Solucionado"
    ]

    cerrados = len(
        tickets[
            tickets["estado"].isin(estados_cerrados)
        ]
    )

    abiertos = total - cerrados

    porcentaje_resolucion = 0

    if total > 0:
        porcentaje_resolucion = round(
            (cerrados / total) * 100,
            1
        )

    return jsonify({
        "total": total,
        "incidentes": incidentes,
        "requerimientos": requerimientos,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "porcentaje_resolucion": porcentaje_resolucion
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )