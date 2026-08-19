let datosAdministradores = [];

let ordenAdministradores = {
    columna: "cantidad",
    direccion: "desc"
};


// ============================================================
// CARGAR ADMINISTRADORES
// ============================================================

async function cargarAdministradores() {

    estadoPagina("Cargando datos...");

    try {

        const p = parametrosFiltros();

        const r = await fetch(
            "/api/administradores?" + p
        );

        const j = await r.json();


        if (!r.ok || !j.ok) {

            throw new Error(
                j.error ||
                "Error cargando Administradores"
            );
        }


        const d = j.data;


        // =====================================================
        // KPIs
        // =====================================================

        document
            .getElementById("totalAdministradores")
            .textContent =
                d.total_administradores;


        document
            .getElementById("totalIncidentes")
            .textContent =
                d.total_incidentes;


        document
            .getElementById("totalRequerimientos")
            .textContent =
                d.total_requerimientos;


        document
            .getElementById("totalTickets")
            .textContent =
                d.total_tickets;


        // =====================================================
        // GRÁFICO
        // =====================================================

        crearGraficoHorizontal(
            "administradores",
            "chartAdministradores",

            d.administradores
                .slice(0, 30)
                .map(
                    x => ({
                        nombre: x.nombre,
                        cantidad: x.cantidad
                    })
                ),

            "Tickets"
        );


        // =====================================================
        // TABLA
        // =====================================================

        datosAdministradores =
            [...d.administradores];


        renderizarTablaAdministradores();


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
// RENDERIZAR TABLA
// ============================================================

function renderizarTablaAdministradores() {

    const t =
        document.getElementById(
            "tablaAdministradores"
        );


    const datos =
        ordenarAdministradores(
            datosAdministradores
        );


    if (!datos.length) {

        t.innerHTML =
            '<tr>' +
            '<td colspan="6" class="empty">' +
            'No hay Administradores Locales para este filtro.' +
            '</td>' +
            '</tr>';

        return;
    }


    t.innerHTML =
        datos.map(
            x => `
                <tr>

                    <td>
                        ${escaparHtml(x.nombre)}
                    </td>

                    <td>
                        ${escaparHtml(x.ministerio)}
                    </td>

                    <td>
                        ${escaparHtml(x.organismo)}
                    </td>

                    <td class="num">
                        ${x.incidentes}
                    </td>

                    <td class="num">
                        ${x.requerimientos}
                    </td>

                    <td class="num">
                        ${x.cantidad}
                    </td>

                </tr>
            `
        ).join("");


    actualizarFlechasAdministradores();
}


// ============================================================
// ORDENAR DATOS
// ============================================================

function ordenarAdministradores(datos) {

    return [...datos].sort(
        (a, b) => {

            let valorA =
                a[ordenAdministradores.columna];

            let valorB =
                b[ordenAdministradores.columna];


            const columnasNumericas = [
                "incidentes",
                "requerimientos",
                "cantidad"
            ];


            if (
                columnasNumericas.includes(
                    ordenAdministradores.columna
                )
            ) {

                valorA =
                    Number(valorA) || 0;

                valorB =
                    Number(valorB) || 0;


                return (
                    ordenAdministradores.direccion === "asc"
                        ? valorA - valorB
                        : valorB - valorA
                );
            }


            valorA =
                String(
                    valorA || ""
                );


            valorB =
                String(
                    valorB || ""
                );


            const resultado =
                valorA.localeCompare(
                    valorB,
                    "es",
                    {
                        sensitivity: "base"
                    }
                );


            return (
                ordenAdministradores.direccion === "asc"
                    ? resultado
                    : -resultado
            );
        }
    );
}


// ============================================================
// FLECHAS
// ============================================================

function actualizarFlechasAdministradores() {

    document
        .querySelectorAll(
            "th.sortable"
        )
        .forEach(
            th => {

                const icono =
                    th.querySelector(
                        ".sort-icon"
                    );


                if (!icono) {
                    return;
                }


                if (
                    th.dataset.columna ===
                    ordenAdministradores.columna
                ) {

                    icono.textContent =
                        ordenAdministradores.direccion === "asc"
                            ? "▲"
                            : "▼";

                } else {

                    icono.textContent =
                        "↕";
                }
            }
        );
}


// ============================================================
// CLICK EN ENCABEZADOS
// ============================================================

function conectarOrdenAdministradores() {

    document
        .querySelectorAll(
            "th.sortable"
        )
        .forEach(
            th => {

                th.addEventListener(
                    "click",
                    () => {

                        const columna =
                            th.dataset.columna;


                        if (
                            ordenAdministradores.columna ===
                            columna
                        ) {

                            ordenAdministradores.direccion =
                                ordenAdministradores.direccion === "asc"
                                    ? "desc"
                                    : "asc";

                        } else {

                            ordenAdministradores.columna =
                                columna;


                            if (
                                columna === "nombre" ||
                                columna === "ministerio" ||
                                columna === "organismo"
                            ) {

                                ordenAdministradores.direccion =
                                    "asc";

                            } else {

                                ordenAdministradores.direccion =
                                    "desc";
                            }
                        }


                        renderizarTablaAdministradores();
                    }
                );
            }
        );
}


// ============================================================
// INICIO
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        conectarOrdenAdministradores();


        try {

            await cargarFiltros();

            await cargarAdministradores();

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
                cargarAdministradores
            );


        document
            .getElementById(
                "btnLimpiar"
            )
            ?.addEventListener(
                "click",
                () =>
                    limpiarFiltros(
                        cargarAdministradores
                    )
            );


        conectarBotonesPeriodos(
            cargarAdministradores
        );
    }
);