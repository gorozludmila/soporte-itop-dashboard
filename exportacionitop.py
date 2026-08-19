from playwright.sync_api import sync_playwright, Page
from pathlib import Path


# =========================
# CONFIGURACIÓN
# =========================

URL = "https://app.santafe.gob.ar/itsm/pages/UI.php?c%5Bmenu%5D=WelcomeMenuPage"

USUARIO = "23462968949"
CONTRASENA = "ConraMaldo04"


# =========================
# CARPETA DATA DEL PROYECTO
# =========================

BASE_DIR = Path(__file__).resolve().parent
CARPETA_DATA = BASE_DIR / "data"

CARPETA_DATA.mkdir(
    parents=True,
    exist_ok=True
)


# =========================
# FUNCIONES GENERALES
# =========================

def abrir_pagina(page: Page):

    print("🌐 Ingresando a ITSM...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60_000
    )

    print("✅ Página cargada")
    print(f"📍 URL actual: {page.url}")


def iniciar_sesion(page: Page):

    print("🔐 Verificando sesión...")

    usuario = page.get_by_placeholder(
        "Ingrese su CUIL o IUP"
    )

    try:

        usuario.wait_for(
            state="visible",
            timeout=3000
        )

    except:

        print("✅ La sesión ya está iniciada")
        print(f"📍 URL actual: {page.url}")

        return

    print("🔐 Completando credenciales...")

    usuario.fill(
        USUARIO
    )

    print("✅ Usuario ingresado")

    password = page.get_by_placeholder(
        "Ingrese su contraseña"
    )

    password.wait_for(
        state="visible",
        timeout=30_000
    )

    password.fill(
        CONTRASENA
    )

    print("✅ Contraseña ingresada")

    boton_login = page.get_by_role(
        "button",
        name="Iniciar sesión"
    )

    boton_login.wait_for(
        state="visible",
        timeout=30_000
    )

    boton_login.click()

    print("✅ Click en Iniciar sesión")

    page.wait_for_load_state(
        "domcontentloaded"
    )

    print(
        f"📍 URL después del login: {page.url}"
    )


def abrir_exportacion_csv(
    page: Page,
    seccion: str
):

    print(f"📂 Entrando a {seccion}...")

    boton_seccion = page.locator(
        "a.summary"
    ).filter(
        has_text=seccion
    )

    boton_seccion.wait_for(
        state="visible",
        timeout=30_000
    )

    boton_seccion.click()

    print(
        f"✅ Sección {seccion} abierta"
    )

    page.wait_for_timeout(1000)

    print("⚙️ Abriendo menú de acciones...")

    otras_acciones = page.get_by_role(
        "button",
        name="Otras Acciones"
    )

    otras_acciones.wait_for(
        state="visible",
        timeout=30_000
    )

    otras_acciones.click()

    print("✅ Menú abierto")

    page.wait_for_timeout(500)

    print("📥 Seleccionando Exportar a CSV...")

    exportar_csv = page.get_by_text(
        "Exportar a CSV...",
        exact=True
    )

    exportar_csv.wait_for(
        state="visible",
        timeout=30_000
    )

    exportar_csv.click()

    print("✅ Click en Exportar a CSV realizado")


# =========================
# FORMULARIO REQUERIMIENTOS
# =========================

def llenar_formulario_requerimientos(page: Page):

    print("📝 Completando formulario de Requerimientos...")

    page.wait_for_timeout(1000)

    # Id (Clave Primaria)
    id_clave_primaria = page.locator(
        "#tfs_interactive_fields_csv_Service_id"
    )

    id_clave_primaria.wait_for(
        state="visible",
        timeout=30_000
    )

    id_clave_primaria.check()

    print("✅ Id (Clave Primaria) seleccionado")

    # Creador
    creador = page.locator(
        "#tfs_interactive_fields_csv_UserRequest_creator_id_multi"
    )

    creador.wait_for(
        state="visible",
        timeout=30_000
    )

    creador.check()

    print("✅ Creador seleccionado")

    # Fecha de Asignación
    fecha_asignacion = page.locator(
        "#tfs_interactive_fields_csv_UserRequest_assignment_date"
    )

    fecha_asignacion.check()

    print("✅ Fecha de Asignación seleccionada")

    # Fecha de Solución
    fecha_solucion = page.locator(
        "#tfs_interactive_fields_csv_UserRequest_resolution_date"
    )

    fecha_solucion.check()

    print("✅ Fecha de Solución seleccionada")

    # Fecha de Cierre
    fecha_cierre = page.locator(
        "#tfs_interactive_fields_csv_UserRequest_close_date"
    )

    fecha_cierre.check()

    print("✅ Fecha de Cierre seleccionada")

    # Fecha de Fin
    fecha_fin = page.locator(
        "#tfs_interactive_fields_csv_UserRequest_end_date"
    )

    fecha_fin.check()

    page.wait_for_timeout(1000)

    print("✅ Fecha de Fin seleccionada")
    print("✅ Campos de Requerimientos seleccionados correctamente")


# =========================
# FORMULARIO INCIDENTES
# =========================

def llenar_formulario_incidentes(page: Page):

    print("📝 Completando formulario de Incidentes...")

    page.wait_for_timeout(1000)

    # Id (Clave Primaria)
    id_clave_primaria = page.locator(
        "#tfs_interactive_fields_csv_Service_id"
    )

    id_clave_primaria.wait_for(
        state="visible",
        timeout=30_000
    )

    id_clave_primaria.check()

    print("✅ Id (Clave Primaria) seleccionado")

    # Creador
    creador = page.locator(
        "#tfs_interactive_fields_csv_Incident_creator_id_multi"
    )

    creador.wait_for(
        state="visible",
        timeout=30_000
    )

    creador.check()

    print("✅ Creador seleccionado")

    # Fecha de Asignación
    fecha_asignacion = page.locator(
        "#tfs_interactive_fields_csv_Incident_assignment_date"
    )

    fecha_asignacion.check()

    print("✅ Fecha de Asignación seleccionada")

    # Fecha de Solución
    fecha_solucion = page.locator(
        "#tfs_interactive_fields_csv_Incident_resolution_date"
    )

    fecha_solucion.check()

    print("✅ Fecha de Solución seleccionada")

    # Fecha de Cierre
    fecha_cierre = page.locator(
        "#tfs_interactive_fields_csv_Incident_close_date"
    )

    fecha_cierre.check()

    print("✅ Fecha de Cierre seleccionada")

    # Fecha de Fin
    fecha_fin = page.locator(
        "#tfs_interactive_fields_csv_Incident_end_date"
    )

    fecha_fin.check()

    page.wait_for_timeout(1000)

    print("✅ Fecha de Fin seleccionada")
    print("✅ Campos de Incidentes seleccionados correctamente")


# =========================
# DESCARGA REQUERIMIENTOS
# =========================

def descargar_requerimientos(page: Page):

    print("📦 Confirmando exportación de Requerimientos...")

    boton_exportar = page.get_by_role(
        "button",
        name="Exportar",
        exact=True
    )

    boton_exportar.wait_for(
        state="visible",
        timeout=30_000
    )

    boton_exportar.click()

    print("✅ Exportación confirmada")
    print("⏳ Esperando enlace de descarga...")

    enlace_descarga = page.get_by_text(
        "Click aquí para descargar",
        exact=False
    )

    enlace_descarga.wait_for(
        state="visible",
        timeout=60_000
    )

    print("✅ Enlace de descarga disponible")

    ruta_archivo = (
        CARPETA_DATA
        / "Requerimiento Exportar.csv"
    )

    if ruta_archivo.exists():

        ruta_archivo.unlink()

        print(
            "🗑️ Requerimiento Exportar.csv anterior eliminado"
        )

    with page.expect_download(
        timeout=30_000
    ) as download_info:

        enlace_descarga.click()

    download = download_info.value

    download.save_as(
        str(ruta_archivo)
    )

    print(
        "✅ Archivo de Requerimientos descargado correctamente"
    )

    print(
        f"📁 Guardado en: {ruta_archivo}"
    )

    return ruta_archivo


# =========================
# DESCARGA INCIDENTES
# =========================

def descargar_incidentes(page: Page):

    print("📦 Confirmando exportación de Incidentes...")

    boton_exportar = page.get_by_role(
        "button",
        name="Exportar",
        exact=True
    )

    boton_exportar.wait_for(
        state="visible",
        timeout=30_000
    )

    boton_exportar.click()

    print("✅ Exportación de Incidentes confirmada")
    print("⏳ Esperando enlace de descarga de Incidentes...")

    enlace_descarga = page.get_by_text(
        "Click aquí para descargar Incidente Exportar.csv",
        exact=False
    )

    enlace_descarga.wait_for(
        state="visible",
        timeout=60_000
    )

    print("✅ Enlace de descarga de Incidentes disponible")

    ruta_archivo = (
        CARPETA_DATA
        / "Incidente Exportar.csv"
    )

    if ruta_archivo.exists():

        ruta_archivo.unlink()

        print(
            "🗑️ Incidente Exportar.csv anterior eliminado"
        )

    with page.expect_download(
        timeout=30_000
    ) as download_info:

        enlace_descarga.click()

    download = download_info.value

    download.save_as(
        str(ruta_archivo)
    )

    print(
        "✅ Archivo de Incidentes descargado correctamente"
    )

    print(
        f"📁 Guardado en: {ruta_archivo}"
    )

    return ruta_archivo


# =========================
# EJECUCIÓN
# =========================

def ejecutar():

    with sync_playwright() as p:

        print("🚀 Iniciando Chrome...")

        navegador = p.chromium.launch(
            headless=False,
            slow_mo=300,
            channel="chrome"
        )

        contexto = navegador.new_context(
            viewport={
                "width": 1100,
                "height": 720
            },
            accept_downloads=True
        )

        try:

            # =====================================
            # REQUERIMIENTOS
            # =====================================

            print("\n")
            print("===========================")
            print("📘 REQUERIMIENTOS")
            print("===========================")
            print("\n")

            page_requerimientos = contexto.new_page()

            abrir_pagina(
                page_requerimientos
            )

            iniciar_sesion(
                page_requerimientos
            )

            abrir_exportacion_csv(
                page_requerimientos,
                "Requerimientos"
            )

            llenar_formulario_requerimientos(
                page_requerimientos
            )

            ruta_requerimientos = descargar_requerimientos(
                page_requerimientos
            )

            print("\n✅ REQUERIMIENTOS TERMINADO")
            print(f"📁 {ruta_requerimientos}")

            # =====================================
            # INCIDENTES
            # =====================================

            print("\n")
            print("===========================")
            print("📕 INCIDENTES")
            print("===========================")
            print("\n")

            print("🆕 Abriendo nueva pestaña...")

            page_incidentes = contexto.new_page()

            abrir_pagina(
                page_incidentes
            )

            iniciar_sesion(
                page_incidentes
            )

            abrir_exportacion_csv(
                page_incidentes,
                "Incidentes"
            )

            llenar_formulario_incidentes(
                page_incidentes
            )

            ruta_incidentes = descargar_incidentes(
                page_incidentes
            )

            print("\n✅ INCIDENTES TERMINADO")
            print(f"📁 {ruta_incidentes}")

            # =====================================
            # FINAL
            # =====================================

            print("\n")
            print("===========================")
            print("🎉 PROCESO COMPLETO")
            print("===========================")

            print("✅ Requerimientos exportados")
            print("✅ Incidentes exportados")

            print("\n📁 ARCHIVOS GENERADOS:")

            print(
                f"📄 {ruta_requerimientos}"
            )

            print(
                f"📄 {ruta_incidentes}"
            )

        except Exception as error:

            print("\n❌ ERROR:")
            print(error)

            raise

        finally:

            navegador.close()


# =========================
# INICIO
# =========================

if __name__ == "__main__":
    ejecutar()