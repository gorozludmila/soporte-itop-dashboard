const btnActualizarDatos = document.getElementById("btnActualizarDatos");
const actualizarTexto = document.getElementById("actualizarTexto");
const actualizarMeta = document.getElementById("actualizarMeta");
const actualizarIcono = document.getElementById("actualizarIcono");


function formatearFechaServidor(valor) {
    if (!valor) {
        return "Sin sincronizar";
    }

    const partes = valor.split(" ");
    const fecha = partes[0]?.split("-");
    const hora = partes[1] || "";

    if (!fecha || fecha.length !== 3) {
        return valor;
    }

    return `${fecha[2]}/${fecha[1]}/${fecha[0]} ${hora}`.trim();
}


async function cargarEstadoSincronizacion() {
    if (!actualizarMeta) {
        return;
    }

    try {
        const respuesta = await fetch("/api/sincronizacion");
        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.ok) {
            throw new Error(datos.error || "No se pudo consultar la sincronización");
        }

        const ultima = datos.data?.ultima_sincronizacion;
        const total = datos.data?.total_tickets ?? 0;

        actualizarMeta.textContent = ultima
            ? `Última actualización: ${formatearFechaServidor(ultima)} · ${total} tickets en SQLite`
            : "Base local todavía sin sincronizar";

    } catch (error) {
        console.error(error);
        actualizarMeta.textContent = "No se pudo consultar la última actualización";
    }
}


if (btnActualizarDatos) {
    btnActualizarDatos.addEventListener("click", async () => {
        try {
            btnActualizarDatos.disabled = true;

            if (actualizarIcono) actualizarIcono.textContent = "⟳";
            if (actualizarTexto) actualizarTexto.textContent = "Actualizando...";
            if (actualizarMeta) actualizarMeta.textContent = "Consultando cambios en iTop...";

            const respuesta = await fetch("/actualizar-datos", {
                method: "POST"
            });

            const datos = await respuesta.json();

            if (!respuesta.ok || !datos.ok) {
                throw new Error(
                    datos.mensaje || "No se pudieron actualizar los datos"
                );
            }

            if (actualizarTexto) actualizarTexto.textContent = "Actualizar datos";

            if (actualizarMeta) {
                actualizarMeta.textContent =
                    `Última actualización: ${datos.fecha} · ` +
                    `${datos.nuevos} nuevos · ${datos.actualizados} actualizados`;
            }

            await cargarFiltros();
            await cargarDashboard();

        } catch (error) {
            console.error(error);

            if (actualizarTexto) actualizarTexto.textContent = "Actualizar datos";
            if (actualizarMeta) actualizarMeta.textContent = "Error al actualizar desde iTop";

            alert(
                "No se pudieron actualizar los datos desde iTop.\n\n" +
                error.message
            );

        } finally {
            if (actualizarIcono) actualizarIcono.textContent = "↻";
            btnActualizarDatos.disabled = false;
        }
    });
}


async function cargarDashboard() {

    estadoPagina("Cargando datos...");

    try {

        const p = parametrosFiltros();

        p.set(
            "agrupacion",
            document.getElementById("agrupacion")?.value || "mes"
        );


        const r = await fetch(
            "/api/resumen?" + p.toString()
        );


        const j = await r.json();


        if (!r.ok || !j.ok) {
            throw new Error(
                j.error || "Error cargando dashboard"
            );
        }


        const d = j.data;


        // =====================================================
        // KPIs
        // =====================================================

        document.getElementById(
            "totalTickets"
        ).textContent = d.total;


        document.getElementById(
            "totalIncidentes"
        ).textContent = d.incidentes;


        document.getElementById(
            "totalRequerimientos"
        ).textContent = d.requerimientos;


        document.getElementById(
            "totalAbiertos"
        ).textContent = d.abiertos;


        document.getElementById(
            "totalCerrados"
        ).textContent = d.cerrados;


        document.getElementById(
            "totalResueltos"
        ).textContent = d.resueltos;


        document.getElementById(
            "porcentaje"
        ).textContent =
            d.porcentaje_resolucion + "%";


        document.getElementById(
            "tiempo"
        ).textContent =
            formatearHoras(
                d.tiempo_promedio_horas
            );


        // =====================================================
        // GRÁFICOS
        // =====================================================

        dibujarEvolucion(
            d.evolucion
        );


        crearGraficoHorizontal(
            "ministerios",
            "chartMinisterios",
            d.ministerios,
            "Tickets"
        );


        crearGraficoHorizontal(
            "organismos",
            "chartOrganismos",
            d.organismos,
            "Tickets"
        );


        crearGraficoHorizontal(
            "servicios",
            "chartServicios",
            d.servicios,
            "Tickets"
        );


        crearGraficoDona(
            "estados",
            "chartEstados",
            d.estados
        );


        crearGraficoDona(
            "origen",
            "chartOrigen",
            [
                {
                    nombre:
                        "Administradores Locales",

                    cantidad:
                        d.origen.administradores
                },

                {
                    nombre:
                        "Otros reportantes",

                    cantidad:
                        d.origen.otros
                }
            ]
        );


        estadoPagina(
            "Datos actualizados correctamente"
        );


    } catch (e) {

        console.error(e);

        estadoPagina(
            e.message,
            true
        );
    }
}



// ============================================================
// FORMATEAR TIEMPO
// ============================================================

function formatearHoras(h) {

    if (!h) {
        return "—";
    }


    if (h < 24) {

        return (
            h.toFixed(1)
            + " h"
        );
    }


    return (
        (h / 24).toFixed(1)
        + " días"
    );
}



// ============================================================
// EVOLUCIÓN TEMPORAL
// ============================================================

function dibujarEvolucion(datos) {

    destruirGrafico(
        "evolucion"
    );


    const c =
        document.getElementById(
            "chartEvolucion"
        );


    if (!c) {
        return;
    }


    graficos.evolucion =
        new Chart(
            c,
            {

                type:
                    "line",


                data: {

                    labels:
                        datos.map(
                            x =>
                                x.periodo
                        ),


                    datasets: [

                        {

                            label:
                                "Recibidos",

                            data:
                                datos.map(
                                    x =>
                                        x.recibidos
                                ),

                            borderColor:
                                "#3277F7",

                            backgroundColor:
                                "rgba(50,119,247,.08)",

                            tension:
                                0.25,

                            borderWidth:
                                3
                        },


                        {

                            label:
                                "Cerrados / solucionados",

                            data:
                                datos.map(
                                    x =>
                                        x.cerrados
                                ),

                            borderColor:
                                "#36A269",

                            backgroundColor:
                                "rgba(54,162,105,.08)",

                            tension:
                                0.25,

                            borderWidth:
                                3
                        }

                    ]
                },


                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,


                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {

                                precision:
                                    0
                            }
                        }
                    },


                    plugins: {

                        legend: {

                            position:
                                "bottom"
                        }
                    }
                }
            }
        );
}



// ============================================================
// INICIO
// ============================================================
document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await cargarFiltros();

            await cargarDashboard();

            await cargarEstadoSincronizacion();

        } catch (e) {

            console.error(e);

            estadoPagina(
                e.message,
                true
            );
        }


        document
            .getElementById(
                "btnFiltrar"
            )
            ?.addEventListener(
                "click",
                cargarDashboard
            );


        document
            .getElementById(
                "btnLimpiar"
            )
            ?.addEventListener(
                "click",
                () =>
                    limpiarFiltros(
                        cargarDashboard
                    )
            );


        document
            .getElementById(
                "agrupacion"
            )
            ?.addEventListener(
                "change",
                cargarDashboard
            );


        conectarBotonesPeriodos(
            cargarDashboard
        );
    }
);