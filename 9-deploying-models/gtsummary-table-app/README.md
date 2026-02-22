# Tabla Descriptiva con gtsummary

Aplicación web de dos capas para generar tablas descriptivas estratificadas a partir de datos clínicos o epidemiológicos. El frontend está construido en Python con Streamlit; el backend expone una API REST escrita en R con Plumber que internamente usa el paquete `gtsummary` para producir las tablas en formato HTML.

---

## Estructura del proyecto

```
gtsummary-table-app/
├── app.py              # Frontend Streamlit
├── plumber_api.R       # Backend: API REST en R
└── README.md
```

---

## Requisitos

### Python

```
Python >= 3.9
streamlit
pandas
requests
openpyxl
```

### R

```
R >= 4.2
plumber
gtsummary
gt
dplyr
jsonlite
```

---

## Instalación

### Dependencias de Python

```bash
pip install streamlit pandas requests openpyxl
```

### Paquetes de R

```r
install.packages(c("plumber", "gtsummary", "gt", "dplyr", "jsonlite"))
```

---

## Ejecución

La aplicación requiere dos procesos corriendo en paralelo: el backend de R y el frontend de Python. Abre dos terminales separadas.

### Terminal 1 — Backend R (Plumber)

```bash
Rscript -e "plumber::plumb('plumber_api.R')\$run(port=8000, host='0.0.0.0')"
```

Para verificar que el servidor está activo, visita:

```
http://localhost:8000/health
```

Deberías recibir una respuesta similar a:

```json
{ "status": "ok" }
```

### Terminal 2 — Frontend Streamlit

```bash
streamlit run app.py
```

La interfaz estará disponible en:

```
http://localhost:8501
```

---

## Flujo de datos

```
Navegador (usuario)
        |
        v
Streamlit app — Python, puerto 8501
        |
        |  POST /tbl_summary
        |  Content-Type: application/json
        |  {
        |    "data": "[{...}]",
        |    "target": "grupo",
        |    "numeric_vars": ["edad", "peso"],
        |    "categorical_vars": ["sexo"],
        |    "factor_config": { ... }
        |  }
        |
        v
Plumber API — R, puerto 8000
        |
        |  tbl_summary() estratificado por target
        |
        v
Respuesta JSON
  { "html": "<table>...</table>", "status": "ok" }
        |
        v
Streamlit renderiza la tabla HTML embebida
```

---

## Referencia de la API

### Endpoint

```
POST http://localhost:8000/tbl_summary
Content-Type: application/json
```

### Cuerpo de la solicitud

```json
{
  "data": "[{\"edad\":25,\"peso\":70.5,\"sexo\":\"M\",\"grupo\":\"caso\"},{\"edad\":34,\"peso\":65.0,\"sexo\":\"F\",\"grupo\":\"control\"}]",
  "target": "grupo",
  "numeric_vars": ["edad", "peso"],
  "categorical_vars": ["sexo"],
  "factor_config": {
    "sexo": {
      "levels": ["M", "F"],
      "labels": ["Masculino", "Femenino"]
    },
    "grupo": {
      "levels": ["control", "caso"],
      "labels": ["Control", "Caso"]
    }
  }
}
```

El campo `data` es el dataset serializado como JSON string (lista de objetos). El campo `factor_config` es opcional: permite definir el orden de los niveles y etiquetas legibles para las variables categóricas y el target.

### Respuesta exitosa

```json
{
  "html": "<html>...<table>...</table>...</html>",
  "status": "ok",
  "n_rows": 100,
  "target": "grupo",
  "vars": {
    "numeric": ["edad", "peso"],
    "categorical": ["sexo"]
  }
}
```

### Respuesta con error

```json
{
  "error": "Descripción del problema",
  "status": "error"
}
```

---

## Consideraciones para producción

| Aspecto | Recomendación |
|---|---|
| CORS | Restringir `Access-Control-Allow-Origin` al dominio del frontend |
| Puertos | Parametrizar con variables de entorno (`PORT`, `HOST`) |
| Logging | Agregar logging estructurado con el paquete `logger` (R) o el módulo `logging` (Python) |
| Autenticación | Proteger el endpoint con una API key en el header de cada solicitud |
| Contenerización | Dockerizar ambos servicios y orquestarlos con `docker-compose` |
| Tamaño de datos | Limitar el dataset de entrada a aproximadamente 50 000 filas para evitar timeouts; implementar paginación o muestreo para volúmenes mayores |