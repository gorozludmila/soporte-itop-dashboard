async function cargarResumen() {

    try {

        const respuesta = await fetch("/api/resumen");

        if (!respuesta.ok) {
            throw new Error("No se pudo obtener el resumen");
        }

        const datos = await respuesta.json();

        document.getElementById("totalTickets").textContent =
            datos.total;

        document.getElementById("totalIncidentes").textContent =
            datos.incidentes;

        document.getElementById("totalRequerimientos").textContent =
            datos.requerimientos;

        document.getElementById("totalAbiertos").textContent =
            datos.abiertos;

        document.getElementById("totalCerrados").textContent =
            datos.cerrados;

        document.getElementById("porcentaje").textContent =
            datos.porcentaje_resolucion + "% resueltos";

        document.getElementById("estadoConexion").textContent =
            "Datos cargados correctamente";

    } catch (error) {

        console.error(error);

        document.getElementById("estadoConexion").textContent =
            "Error al cargar los datos";
    }
}


document.addEventListener(
    "DOMContentLoaded",
    cargarResumen
);