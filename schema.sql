CREATE TABLE IF NOT EXISTS tickets (
    referencia TEXT PRIMARY KEY,
    clase_itop TEXT NOT NULL,
    itop_id INTEGER,
    tipo TEXT NOT NULL,
    asunto TEXT NOT NULL DEFAULT '',
    organizacion TEXT NOT NULL DEFAULT '',
    reportado_por TEXT NOT NULL DEFAULT '',
    analista TEXT NOT NULL DEFAULT '',
    servicio TEXT NOT NULL DEFAULT '',
    estado TEXT NOT NULL DEFAULT '',
    estado_operativo TEXT NOT NULL DEFAULT '',
    fecha_inicio TEXT,
    fecha_asignacion TEXT,
    fecha_solucion TEXT,
    fecha_cierre TEXT,
    fecha_fin TEXT,
    fecha_real_solucion TEXT,
    last_update_itop TEXT,
    sincronizado_en TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_tickets_clase_id
ON tickets(clase_itop, itop_id)
WHERE itop_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tickets_tipo ON tickets(tipo);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha_inicio ON tickets(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_tickets_last_update ON tickets(last_update_itop);

CREATE TABLE IF NOT EXISTS sync_control (
    clase_itop TEXT PRIMARY KEY,
    ultima_actualizacion_itop TEXT,
    ultima_sincronizacion TEXT NOT NULL,
    cantidad_ultima_sync INTEGER NOT NULL DEFAULT 0
);
