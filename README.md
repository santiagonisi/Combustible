# Combustible

Sistema de gestión y control del consumo de combustible para operaciones de la empresa.

## Stack

- **Backend:** Python + FastAPI
- **Persistencia:** SQLAlchemy + SQLite
- **Validación de datos:** Pydantic
- **Interfaz web:** Jinja2
- **Reportes:** ReportLab (PDF)
- **Servidor:** Uvicorn / Gunicorn

## Estructura del proyecto

```
Combustible/
├── src/
│   ├── api/              # Rutas y endpoints de la aplicación
│   ├── core/             # Configuración general
│   ├── db/               # Conexión y persistencia de datos
│   ├── models/           # Modelos de base de datos
│   ├── schemas/          # Esquemas de validación
│   ├── services/         # Lógica de negocio
│   └── web/              # Plantillas y recursos de la interfaz
├── tests/                # Pruebas automatizadas
├── backups/              # Copias de seguridad locales
├── requirements.txt      # Dependencias de Python
└── run.ps1               # Script de ejecución
```

## Módulos

- **Consumo de combustible:** registro y consulta de consumos.
- **API REST:** exposición de los recursos del sistema.
- **Persistencia:** gestión de datos mediante SQLAlchemy y SQLite.
- **Reportes:** generación de informes en formato PDF.
- **Interfaz web:** consulta y administración de la información.
