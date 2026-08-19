let graficos = {};
let filtrosCache = null;


// ============================================================
// DESTRUIR GRÁFICOS
// ============================================================

function destruirGrafico(nombre) {

    if (graficos[nombre]) {

        graficos[nombre].destroy();

        delete graficos[nombre];
    }
}


// ============================================================
// PLUGIN - VALORES SOBRE LAS BARRAS
// ============================================================

const pluginValoresBarras = {

    id: "pluginValoresBarras",

    afterDatasetsDraw(chart) {

        if (chart.config.type !== "bar") {
            return;
        }

        const {
            ctx,
            chartArea
        } = chart;

        ctx.save();

        ctx.font =
            "700 12px Segoe UI, Arial";

        ctx.fillStyle =
            "#175fd8";

        ctx.textBaseline =
            "middle";


        chart.data.datasets.forEach(
            (dataset, datasetIndex) => {

                const meta =
                    chart.getDatasetMeta(
                        datasetIndex
                    );


                meta.data.forEach(
                    (barra, index) => {

                        const valor =
                            dataset.data[index];


                        if (
                            valor === null ||
                            valor === undefined
                        ) {
                            return;
                        }


                        if (
                            chart.options.indexAxis === "y"
                        ) {

                            ctx.textAlign =
                                "left";

                            const x =
                                Math.min(
                                    barra.x + 7,
                                    chartArea.right + 18
                                );

                            ctx.fillText(
                                String(valor),
                                x,
                                barra.y
                            );

                        } else {

                            ctx.textAlign =
                                "center";

                            ctx.fillText(
                                String(valor),
                                barra.x,
                                barra.y - 9
                            );
                        }
                    }
                );
            }
        );

        ctx.restore();
    }
};


// ============================================================
// GRÁFICO HORIZONTAL
// ============================================================

function crearGraficoHorizontal(
    nombre,
    canvasId,
    datos,
    etiqueta,
    onClick = null
) {

    destruirGrafico(nombre);


    const canvas =
        document.getElementById(
            canvasId
        );


    if (!canvas) {
        return;
    }


    graficos[nombre] =
        new Chart(
            canvas,
            {

                type: "bar",

                plugins: [
                    pluginValoresBarras
                ],

                data: {

                    labels:
                        (datos || [])
                            .map(
                                x => x.nombre
                            ),

                    datasets: [

                        {

                            label:
                                etiqueta,

                            data:
                                (datos || [])
                                    .map(
                                        x => x.cantidad
                                    ),

                            backgroundColor:
                                "rgba(76,158,218,.65)",

                            borderWidth:
                                0,

                            borderRadius:
                                7,

                            barPercentage:
                                .72,

                            categoryPercentage:
                                .84
                        }
                    ]
                },


                options: {

                    indexAxis:
                        "y",

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    layout: {

                        padding: {
                            right: 35
                        }
                    },

                    onClick:
                        onClick || undefined,

                    plugins: {

                        legend: {
                            display: false
                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    c =>
                                        `${etiqueta}: ${c.raw}`
                            }
                        }
                    },

                    scales: {

                        x: {

                            beginAtZero:
                                true,

                            grace:
                                "10%",

                            ticks: {
                                precision: 0
                            },

                            grid: {
                                color:
                                    "rgba(0,0,0,.07)"
                            }
                        },

                        y: {

                            grid: {
                                display: false
                            },

                            ticks: {

                                color:
                                    "#5f6471",

                                font: {
                                    size: 11
                                }
                            }
                        }
                    }
                }
            }
        );
}


// ============================================================
// GRÁFICO DONA
// ============================================================

function crearGraficoDona(
    nombre,
    canvasId,
    datos
) {

    destruirGrafico(nombre);


    const canvas =
        document.getElementById(
            canvasId
        );


    if (!canvas) {
        return;
    }


    graficos[nombre] =
        new Chart(
            canvas,
            {

                type:
                    "doughnut",

                data: {

                    labels:
                        (datos || [])
                            .map(
                                x => x.nombre
                            ),

                    datasets: [

                        {

                            data:
                                (datos || [])
                                    .map(
                                        x => x.cantidad
                                    ),

                            backgroundColor: [

                                "#6D45B5",
                                "#F39B22",
                                "#D94B83",
                                "#3277F7",
                                "#36A269",
                                "#9aa0b2"

                            ],

                            borderColor:
                                "#fff",

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

                    cutout:
                        "62%",

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
// PARÁMETROS DE FILTROS
// ============================================================

function parametrosFiltros() {

    const params =
        new URLSearchParams();


    [
        "desde",
        "hasta",
        "ministerio",
        "organismo",
        "tipo",
        "estado",
        "servicio",
        "persona_tipo",
        "persona"

    ].forEach(
        id => {

            const el =
                document.getElementById(id);


            if (
                el &&
                el.value
            ) {

                params.set(
                    id,
                    el.value
                );
            }
        }
    );


    return params;
}


// ============================================================
// LLENAR SELECT
// ============================================================

function llenarSelect(
    id,
    valores,
    textoTodos = "Todos"
) {

    const select =
        document.getElementById(id);


    if (!select) {
        return;
    }


    const actual =
        select.value;


    select.innerHTML =
        `<option value="">${textoTodos}</option>`;


    (valores || []).forEach(
        valor => {

            const op =
                document.createElement(
                    "option"
                );


            if (
                typeof valor === "object"
            ) {

                op.value =
                    valor.value;

                op.textContent =
                    valor.label;

            } else {

                op.value =
                    valor;

                op.textContent =
                    valor;
            }


            select.appendChild(op);
        }
    );


    if (
        [...select.options]
            .some(
                o => o.value === actual
            )
    ) {

        select.value =
            actual;
    }
}


// ============================================================
// PERSONAS
// ============================================================

function actualizarPersonas() {

    const tipo =
        document.getElementById(
            "persona_tipo"
        );

    const persona =
        document.getElementById(
            "persona"
        );


    if (
        !tipo ||
        !persona ||
        !filtrosCache
    ) {
        return;
    }


    // Al cambiar el tipo de persona
    // eliminamos la selección anterior

    persona.value = "";


    llenarSelect(
        "persona",
        filtrosCache.personas?.[
            tipo.value
        ] || [],
        "Todas"
    );
}


// ============================================================
// ORGANISMOS SEGÚN MINISTERIO
// ============================================================

function actualizarOrganismos() {

    const ministerio =
        document.getElementById(
            "ministerio"
        );

    const organismo =
        document.getElementById(
            "organismo"
        );


    if (
        !ministerio ||
        !organismo ||
        !filtrosCache
    ) {
        return;
    }


    // Si cambia el Ministerio,
    // eliminamos el Organismo anterior

    organismo.value = "";


    const organismos =
        ministerio.value

            ? (
                filtrosCache
                    .organismos_por_ministerio?.[
                        ministerio.value
                    ] || []
            )

            : (
                filtrosCache.organismos || []
            );


    llenarSelect(
        "organismo",
        organismos
    );
}


// ============================================================
// CARGAR FILTROS
// ============================================================

async function cargarFiltros() {

    const r =
        await fetch(
            "/api/filtros"
        );


    const json =
        await r.json();


    if (
        !r.ok ||
        !json.ok
    ) {

        throw new Error(
            json.error ||
            "No se pudieron cargar los filtros."
        );
    }


    filtrosCache =
        json.data;


    // --------------------------------------------------------
    // MINISTERIOS
    // --------------------------------------------------------

    llenarSelect(
        "ministerio",
        filtrosCache.ministerios || []
    );


    // --------------------------------------------------------
    // ORGANISMOS
    // --------------------------------------------------------

    llenarSelect(
        "organismo",
        filtrosCache.organismos || []
    );


    // --------------------------------------------------------
    // ESTADOS
    // --------------------------------------------------------

    const estados = [

        {
            value:
                "__abiertos__",

            label:
                "Abiertos"
        },

        {
            value:
                "__finalizados__",

            label:
                "Cerrados / solucionados"
        },

        ...(
            filtrosCache.estados || []
        )

    ];


    llenarSelect(
        "estado",
        estados
    );


    // --------------------------------------------------------
    // SERVICIOS
    // --------------------------------------------------------

    llenarSelect(
        "servicio",
        filtrosCache.servicios || []
    );


    // --------------------------------------------------------
    // PERSONAS
    // --------------------------------------------------------

    actualizarPersonas();


    // --------------------------------------------------------
    // EVENTO MINISTERIO -> ORGANISMO
    // --------------------------------------------------------

    const ministerio =
        document.getElementById(
            "ministerio"
        );


    if (
        ministerio &&
        !ministerio.dataset.listener
    ) {

        ministerio.addEventListener(
            "change",
            actualizarOrganismos
        );


        ministerio.dataset.listener =
            "1";
    }


    // --------------------------------------------------------
    // EVENTO TIPO PERSONA -> NOMBRE
    // --------------------------------------------------------

    const tipoPersona =
        document.getElementById(
            "persona_tipo"
        );


    if (
        tipoPersona &&
        !tipoPersona.dataset.listener
    ) {

        tipoPersona.addEventListener(
            "change",
            actualizarPersonas
        );


        tipoPersona.dataset.listener =
            "1";
    }
}


// ============================================================
// ESTADO DE LA PÁGINA
// ============================================================

function estadoPagina(
    texto,
    error = false
) {

    const el =
        document.getElementById(
            "estadoConexion"
        );


    if (!el) {
        return;
    }


    el.classList.toggle(
        "error",
        error
    );


    el.innerHTML =
        `<span class="status-dot"></span>${texto}`;
}


// ============================================================
// FECHAS
// ============================================================

function isoFecha(d) {

    const copia =
        new Date(
            d.getTime() -
            d.getTimezoneOffset() * 60000
        );


    return copia
        .toISOString()
        .slice(0, 10);
}


// ============================================================
// ESTABLECER PERÍODO
// ============================================================

function setPeriodo(periodo) {

    const desde =
        document.getElementById(
            "desde"
        );

    const hasta =
        document.getElementById(
            "hasta"
        );


    if (
        !desde ||
        !hasta
    ) {
        return;
    }


    const hoy =
        new Date();


    let inicio =
        new Date(hoy);


    // --------------------------------------------------------
    // SEMANA ACTUAL
    // --------------------------------------------------------

    if (
        periodo === "semana"
    ) {

        const dia =
            (hoy.getDay() + 6) % 7;


        inicio.setDate(
            hoy.getDate() - dia
        );


    // --------------------------------------------------------
    // MES ACTUAL
    // --------------------------------------------------------

    } else if (
        periodo === "mes"
    ) {

        inicio =
            new Date(
                hoy.getFullYear(),
                hoy.getMonth(),
                1
            );


    // --------------------------------------------------------
    // AÑO ACTUAL
    // --------------------------------------------------------

    } else if (
        periodo === "anio"
    ) {

        inicio =
            new Date(
                hoy.getFullYear(),
                0,
                1
            );
    }


    desde.value =
        isoFecha(inicio);


    hasta.value =
        isoFecha(hoy);


    marcarPeriodoActivo(
        periodo
    );
}


// ============================================================
// MARCAR BOTÓN DE PERÍODO ACTIVO
// ============================================================

function marcarPeriodoActivo(
    periodo
) {

    document
        .querySelectorAll(
            "[data-periodo]"
        )
        .forEach(
            btn => {

                btn.classList.toggle(
                    "active",
                    btn.dataset.periodo === periodo
                );
            }
        );
}


// ============================================================
// CONECTAR BOTONES DE PERÍODO
// ============================================================

function conectarBotonesPeriodos(
    callback
) {

    document
        .querySelectorAll(
            "[data-periodo]"
        )
        .forEach(
            btn => {

                // Evita registrar el mismo listener
                // más de una vez

                if (
                    btn.dataset.periodoListener
                ) {
                    return;
                }


                btn.addEventListener(
                    "click",
                    async () => {

                        setPeriodo(
                            btn.dataset.periodo
                        );


                        if (callback) {

                            await callback();
                        }
                    }
                );


                btn.dataset.periodoListener =
                    "1";
            }
        );
}


// ============================================================
// LIMPIAR FILTROS
// ============================================================

async function limpiarFiltros(
    callback
) {

    document
        .querySelectorAll(
            ".toolbar input, .toolbar select"
        )
        .forEach(
            el => {

                if (
                    el.id ===
                    "persona_tipo"
                ) {

                    el.value =
                        "reportado";

                } else {

                    el.value =
                        "";
                }
            }
        );


    // Restaurar todos los organismos
    // y todas las personas

    if (filtrosCache) {

        llenarSelect(
            "organismo",
            filtrosCache.organismos || []
        );


        actualizarPersonas();
    }


    // Sacar selección visual
    // Semana / Mes / Año

    marcarPeriodoActivo(
        null
    );


    if (callback) {

        await callback();
    }
}


// ============================================================
// ESCAPAR HTML
// ============================================================

function escaparHtml(v) {

    return String(
        v ?? ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}