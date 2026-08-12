# Dashboard Soporte iTop - UGD

El proyecto lee directamente los CSV. No usa base de datos.

## Datos

Primero busca los archivos en:

`/home/usuario/Documentos/PROYECTO`

Si no están ahí, usa la carpeta `data/` incluida en el proyecto.

Archivos esperados:

- `Incidente Exportar.csv`
- `Requerimiento Exportar.csv`
- `Jefe_de_Sectoriales_con_sus_Usuarios.csv`

## Ejecutar en Ubuntu

```bash
cd ~/Documentos/soporte-itop-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir en la PC servidor:

`http://127.0.0.1:4000`

Desde otra PC de la misma red:

`http://IP_DEL_SERVIDOR:4000`

## Nota sobre datos no disponibles

Los CSV actuales no incluyen información suficiente para calcular SLA ni el campo Creador. El dashboard no inventa esos valores.
