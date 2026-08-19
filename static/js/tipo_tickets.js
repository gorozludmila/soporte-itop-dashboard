async function cargarTipo(){
    
    estadoPagina("Cargando datos...");
    try{const p=parametrosFiltros();
        p.set("solo_tipo",window.TIPO_TICKET);

        p.set(
    "agrupacion",
    document.getElementById("agrupacion")?.value || "mes"
);
        const r=await fetch("/api/tickets?"+p);
        const j=await r.json();
        if(!r.ok||!j.ok)
            throw new Error(j.error||"Error cargando tickets");
        const d=j.data;
        dibujarEvolucion(d.evolucion);
        document.getElementById("tipoTotal").textContent=d.total;document.getElementById("tipoAbiertos").textContent=d.abiertos;document.getElementById("tipoCerrados").textContent=d.cerrados;document.getElementById("tipoResueltos").textContent=d.resueltos;crearGraficoHorizontal("organismos","chartOrganismos",d.por_organismo,window.TIPO_PLURAL);
        crearGraficoHorizontal("servicios","chartServicios",d.por_servicio,window.TIPO_PLURAL);crearGraficoHorizontal("ministerios","chartMinisterios",d.por_ministerio,window.TIPO_PLURAL);
        crearGraficoDona("estados","chartEstados",d.por_estado);crearGraficoHorizontal("admins","chartAdmins",d.por_admin.map(x=>({nombre:x.nombre,cantidad:x.cantidad})),window.TIPO_PLURAL);crearGraficoHorizontal("reportantes","chartReportantes",d.por_reportante,window.TIPO_PLURAL);
        llenarTablaAdmins(d.por_admin);
        estadoPagina("Datos actualizados correctamente");}
        catch(e){console.error(e);
            estadoPagina(e.message,true);}}
function llenarTablaAdmins(datos){const t=document.getElementById("tablaAdministradores");if(!t)return;if(!datos.length){t.innerHTML='<tr><td colspan="4" class="empty">No hay Administradores Locales para este filtro.</td></tr>';return;}t.innerHTML=datos.map(x=>`<tr><td>${escaparHtml(x.nombre)}</td><td>${escaparHtml(x.ministerio)}</td><td>${escaparHtml(x.organismo)}</td><td class="num">${x.cantidad}</td></tr>`).join("");}
document.addEventListener("DOMContentLoaded",async()=>{try{await cargarFiltros();await cargarTipo();}catch(e){console.error(e);estadoPagina(e.message,true);}document.getElementById("btnFiltrar")?.addEventListener("click",cargarTipo);document.getElementById("btnLimpiar")?.addEventListener("click",()=>limpiarFiltros(cargarTipo));conectarBotonesPeriodos(cargarTipo);});




function dibujarEvolucion(datos) {

    destruirGrafico("evolucion");

    const c = document.getElementById("chartEvolucion");

    if (!c) {
        return;
    }

    graficos.evolucion = new Chart(c, {

        type: "line",

        data: {

            labels: datos.map(
                x => x.periodo
            ),

            datasets: [

                {
                    label: "Recibidos",

                    data: datos.map(
                        x => x.recibidos
                    ),

                    borderColor: "#3277F7",
                    backgroundColor: "rgba(50,119,247,.08)",
                    tension: 0.25,
                    borderWidth: 3
                },

                {
                    label: "Cerrados / solucionados",

                    data: datos.map(
                        x => x.cerrados
                    ),

                    borderColor: "#36A269",
                    backgroundColor: "rgba(54,162,105,.08)",
                    tension: 0.25,
                    borderWidth: 3
                }
            ]
        },

        options: {

            responsive: true,
            maintainAspectRatio: false,

            scales: {

                y: {
                    beginAtZero: true,

                    ticks: {
                        precision: 0
                    }
                }
            },

            plugins: {

                legend: {
                    position: "bottom"
                }
            }
        }
    });
}