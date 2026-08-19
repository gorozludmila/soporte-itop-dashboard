let listaMinisterios = [];


// ============================================================
// DATOS Y ORDEN DE TABLAS
// ============================================================

let datosTablas = {
    organismos: [],
    adminsIncidentes: [],
    adminsRequerimientos: []
};


let ordenTablas = {

    organismos: {
        columna: "total",
        direccion: "desc"
    },

    adminsIncidentes: {
        columna: "cantidad",
        direccion: "desc"
    },

    adminsRequerimientos: {
        columna: "cantidad",
        direccion: "desc"
    }

};


// ============================================================
// CARGAR MINISTERIOS
// ============================================================

async function cargarMinisterios() {

    estadoPagina("Cargando datos...");

    try {

        const p = parametrosFiltros();

        const r = await fetch(
            "/api/ministerios?" + p
        );

        const j = await r.json();


        if (!r.ok || !j.ok) {
            throw new Error(
                j.error || "Error cargando Ministerios"
            );
        }


        listaMinisterios =
            j.data.ministerios;


        crearGraficoHorizontal(
            "ministerios",
            "chartMinisterios",

            listaMinisterios.map(
                x => ({
                    nombre: x.ministerio,
                    cantidad: x.total
                })
            ),

            "Tickets",

            (evento, elementos) => {

                if (!elementos.length) {
                    return;
                }

                cargarDetalleMinisterio(
                    listaMinisterios[
                        elementos[0].index
                    ].ministerio
                );
            }
        );


        estadoPagina(
            "Hacé clic en un Ministerio para ver el detalle"
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
// DETALLE DE MINISTERIO
// ============================================================

async function cargarDetalleMinisterio(ministerio) {

    estadoPagina(
        "Cargando detalle..."
    );

    try {

        const p = parametrosFiltros();

        p.set(
            "ministerio",
            ministerio
        );


        const r = await fetch(
            "/api/ministerios/detalle?" + p
        );

        const j = await r.json();


        if (!r.ok || !j.ok) {

            throw new Error(
                j.error ||
                "Error detalle Ministerio"
            );
        }


        const d = j.data;


        document
            .getElementById(
                "detalleMinisterio"
            )
            .classList.remove(
                "hidden"
            );


        document
            .getElementById(
                "nombreMinisterio"
            )
            .textContent =
                d.ministerio;


        document
            .getElementById(
                "ministerioTotal"
            )
            .textContent =
                d.resumen.total;


        document
            .getElementById(
                "ministerioIncidentes"
            )
            .textContent =
                d.resumen.incidentes;


        document
            .getElementById(
                "ministerioRequerimientos"
            )
            .textContent =
                d.resumen.requerimientos;


        document
            .getElementById(
                "ministerioAbiertos"
            )
            .textContent =
                d.resumen.abiertos;


        document
            .getElementById(
                "ministerioCerrados"
            )
            .textContent =
                d.resumen.finalizados;


        llenarOrganismos(
            d.organismos
        );


        llenarAdmins(
            "tablaAdminsIncidentes",
            d.admins_incidentes
        );


        llenarAdmins(
            "tablaAdminsRequerimientos",
            d.admins_requerimientos
        );


        estadoPagina(
            "Detalle actualizado"
        );


        document
            .getElementById(
                "detalleMinisterio"
            )
            .scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


    } catch (e) {

        console.error(e);

        estadoPagina(
            e.message,
            true
        );
    }
}


// ============================================================
// ORGANISMOS
// ============================================================

function llenarOrganismos(datos) {

    datosTablas.organismos =
        [...datos];

    renderizarOrganismos();
}


function renderizarOrganismos() {

    const t =
        document.getElementById(
            "tablaOrganismos"
        );


    const datos =
        ordenarDatos(
            datosTablas.organismos,
            ordenTablas.organismos
        );


    if (!datos.length) {

        t.innerHTML =
            '<tr>' +
            '<td colspan="7" class="empty">' +
            'Sin organismos.' +
            '</td>' +
            '</tr>';

        return;
    }


    t.innerHTML =
        datos.map(
            x => `
                <tr data-organismo="${encodeURIComponent(x.organismo)}">

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
                        ${x.abiertos}
                    </td>

                    <td class="num">
                        ${x.cerrados}
                    </td>

                    <td class="num">
                        ${x.resueltos}
                    </td>

                    <td class="num">
                        ${x.total}
                    </td>

                </tr>
            `
        ).join("");


    t
        .querySelectorAll(
            "tr[data-organismo]"
        )
        .forEach(
            tr => {

                tr.addEventListener(
                    "click",
                    () => {

                        cargarDetalleOrganismo(
                            decodeURIComponent(
                                tr.dataset.organismo
                            )
                        );
                    }
                );
            }
        );


    actualizarFlechasTabla(
        "organismos"
    );
}


// ============================================================
// ADMINISTRADORES
// ============================================================

function llenarAdmins(
    id,
    datos
) {

    let nombreTabla;


    if (
        id ===
        "tablaAdminsIncidentes"
    ) {

        nombreTabla =
            "adminsIncidentes";

    } else {

        nombreTabla =
            "adminsRequerimientos";
    }


    datosTablas[nombreTabla] =
        [...datos];


    renderizarAdmins(
        id,
        nombreTabla
    );
}


function renderizarAdmins(
    id,
    nombreTabla
) {

    const t =
        document.getElementById(
            id
        );


    const datos =
        ordenarDatos(
            datosTablas[nombreTabla],
            ordenTablas[nombreTabla]
        );


    if (!datos.length) {

        t.innerHTML =
            '<tr>' +
            '<td colspan="3" class="empty">' +
            'Sin Administradores Locales.' +
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
                        ${escaparHtml(x.organismo)}
                    </td>

                    <td class="num">
                        ${x.cantidad}
                    </td>

                </tr>
            `
        ).join("");


    actualizarFlechasTabla(
        nombreTabla
    );
}


// ============================================================
// ORDENAMIENTO
// ============================================================

function ordenarDatos(
    datos,
    orden
) {

    return [...datos].sort(
        (a, b) => {

            let valorA =
                a[orden.columna];

            let valorB =
                b[orden.columna];


            const columnasNumericas = [
                "cantidad",
                "total",
                "incidentes",
                "requerimientos",
                "abiertos",
                "cerrados",
                "resueltos"
            ];


            if (
                columnasNumericas.includes(
                    orden.columna
                )
            ) {

                valorA =
                    Number(valorA) || 0;

                valorB =
                    Number(valorB) || 0;


                return (
                    orden.direccion === "asc"
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
                orden.direccion === "asc"
                    ? resultado
                    : -resultado
            );
        }
    );
}


// ============================================================
// FLECHAS
// ============================================================

function actualizarFlechasTabla(
    nombreTabla
) {

    document
        .querySelectorAll(
            `th.sortable[data-tabla="${nombreTabla}"]`
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
                    ordenTablas[nombreTabla].columna
                ) {

                    icono.textContent =
                        ordenTablas[nombreTabla]
                            .direccion === "asc"
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

function conectarOrdenTablas() {

    document
        .querySelectorAll(
            "th.sortable"
        )
        .forEach(
            th => {

                th.addEventListener(
                    "click",
                    () => {

                        const nombreTabla =
                            th.dataset.tabla;

                        const columna =
                            th.dataset.columna;


                        const orden =
                            ordenTablas[
                                nombreTabla
                            ];


                        if (!orden) {
                            return;
                        }


                        if (
                            orden.columna ===
                            columna
                        ) {

                            orden.direccion =
                                orden.direccion ===
                                "asc"
                                    ? "desc"
                                    : "asc";

                        } else {

                            orden.columna =
                                columna;


                            if (
                                columna === "nombre" ||
                                columna === "organismo"
                            ) {

                                orden.direccion =
                                    "asc";

                            } else {

                                orden.direccion =
                                    "desc";
                            }
                        }


                        if (
                            nombreTabla ===
                            "organismos"
                        ) {

                            renderizarOrganismos();

                        } else if (
                            nombreTabla ===
                            "adminsIncidentes"
                        ) {

                            renderizarAdmins(
                                "tablaAdminsIncidentes",
                                nombreTabla
                            );

                        } else if (
                            nombreTabla ===
                            "adminsRequerimientos"
                        ) {

                            renderizarAdmins(
                                "tablaAdminsRequerimientos",
                                nombreTabla
                            );
                        }
                    }
                );
            }
        );
}


// ============================================================
// DETALLE DE ORGANISMO
// ============================================================

async function cargarDetalleOrganismo(
    organismo
) {

    estadoPagina(
        "Cargando Organismo..."
    );

    try {

        const p =
            parametrosFiltros();


        p.set(
            "organismo",
            organismo
        );


        const r =
            await fetch(
                "/api/organismos/detalle?"
                + p
            );


        const j =
            await r.json();


        if (!r.ok || !j.ok) {

            throw new Error(
                j.error ||
                "Error detalle Organismo"
            );
        }


        const d = j.data;


        document
            .getElementById(
                "detalleOrganismo"
            )
            .classList.remove(
                "hidden"
            );


        document
            .getElementById(
                "nombreOrganismo"
            )
            .textContent =
                d.organismo;


        document
            .getElementById(
                "organismoTotal"
            )
            .textContent =
                d.resumen.total;


        document
            .getElementById(
                "organismoIncidentes"
            )
            .textContent =
                d.resumen.incidentes;


        document
            .getElementById(
                "organismoRequerimientos"
            )
            .textContent =
                d.resumen.requerimientos;


        document
            .getElementById(
                "organismoAbiertos"
            )
            .textContent =
                d.resumen.abiertos;


        const fill =
            (id, arr) => {

                document
                    .getElementById(
                        id
                    )
                    .innerHTML =
                        arr.length
                            ? arr.map(
                                x => `
                                    <tr>

                                        <td>
                                            ${escaparHtml(x.nombre)}
                                        </td>

                                        <td class="num">
                                            ${x.cantidad}
                                        </td>

                                    </tr>
                                `
                            ).join("")
                            : (
                                '<tr>' +
                                '<td colspan="2" class="empty">' +
                                'Sin datos.' +
                                '</td>' +
                                '</tr>'
                            );
            };


        fill(
            "orgAdminsInc",
            d.admins_incidentes
        );


        fill(
            "orgAdminsReq",
            d.admins_requerimientos
        );


        document
            .getElementById(
                "detalleOrganismo"
            )
            .scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


        estadoPagina(
            "Detalle del Organismo actualizado"
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
// INICIO
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        conectarOrdenTablas();


        try {

            await cargarFiltros();

            await cargarMinisterios();

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
                cargarMinisterios
            );


        document
            .getElementById(
                "btnLimpiar"
            )
            ?.addEventListener(
                "click",
                () =>
                    limpiarFiltros(
                        cargarMinisterios
                    )
            );


        conectarBotonesPeriodos(
            cargarMinisterios
        );
    }
);