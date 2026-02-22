# ─────────────────────────────────────────────────────────────────────────────
# API Plumber — Tabla descriptiva con gtsummary
# Archivo: plumber_api.R
# Uso: Rscript -e "plumber::plumb('plumber_api.R')$run(port=8000, host='0.0.0.0')"
# ─────────────────────────────────────────────────────────────────────────────

library(plumber)
library(gtsummary)
library(dplyr)
library(jsonlite)
library(gt)

# ── CORS ─────────────────────────────────────────────────────────────────────
#* @filter cors
function(req, res) {
  res$setHeader("Access-Control-Allow-Origin", "*")
  res$setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
  res$setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization")
  if (req$REQUEST_METHOD == "OPTIONS") {
    res$status <- 200
    return(list())
  }
  plumber::forward()
}

# ─────────────────────────────────────────────────────────────────────────────
# Endpoint principal
# ─────────────────────────────────────────────────────────────────────────────

#* Genera una tabla descriptiva tbl_summary estratificada por la variable target
#* @post /tbl_summary
#* @serializer json
function(req, res) {

  # ── 1. Parsear body ───────────────────────────────────────────────────────
  body <- tryCatch(
    jsonlite::fromJSON(req$postBody, simplifyVector = TRUE),
    error = function(e) NULL
  )

  if (is.null(body)) {
    res$status <- 400
    return(list(error = "No se pudo parsear el cuerpo de la peticion. Envia JSON valido."))
  }

  # ── 2. Extraer parametros ─────────────────────────────────────────────────
  target           <- body$target
  numeric_vars     <- body$numeric_vars     # character vector o NULL
  categorical_vars <- body$categorical_vars # character vector o NULL

  # factor_config: lista con nombres de columna → {levels, labels}
  # Ejemplo: list(sexo = list(levels=c("M","F"), labels=c("Masculino","Femenino")))
  factor_config <- body$factor_config       # puede ser NULL

  # Dataset
  df <- tryCatch(
    jsonlite::fromJSON(body$data, simplifyDataFrame = TRUE),
    error = function(e) NULL
  )

  if (is.null(df) || nrow(df) == 0) {
    res$status <- 400
    return(list(error = "El dataset recibido esta vacio o no es valido."))
  }

  # ── 3. Validaciones ───────────────────────────────────────────────────────
  if (is.null(target) || !target %in% names(df)) {
    res$status <- 400
    return(list(error = paste("La variable target '", target, "' no existe en el dataset.")))
  }

  n_unique <- length(unique(na.omit(df[[target]])))
  if (n_unique != 2) {
    res$status <- 422
    return(list(
      error = paste0(
        "La variable target '", target,
        "' no es binaria (tiene ", n_unique, " valores unicos). ",
        "Se requieren exactamente 2."
      )
    ))
  }

  all_feature_vars <- c(numeric_vars, categorical_vars)
  if (length(all_feature_vars) == 0) {
    res$status <- 400
    return(list(error = "Debes seleccionar al menos una variable numerica o categorica."))
  }

  missing_vars <- setdiff(all_feature_vars, names(df))
  if (length(missing_vars) > 0) {
    res$status <- 400
    return(list(error = paste("Variables no encontradas en el dataset:", paste(missing_vars, collapse = ", "))))
  }

  # ── 4. Preparar el dataframe ──────────────────────────────────────────────
  df_work <- df[, c(target, all_feature_vars), drop = FALSE]

  # Helper: convierte una columna a factor con config personalizada o automatica
  make_factor <- function(col_values, col_name) {
    cfg <- if (!is.null(factor_config)) factor_config[[col_name]] else NULL

    if (!is.null(cfg) && !is.null(cfg$levels) && length(cfg$levels) > 0) {
      # Usar niveles y etiquetas definidos por el usuario
      lvls   <- as.character(unlist(cfg$levels))
      lbls   <- as.character(unlist(cfg$labels))

      # Si labels no fue provisto o esta incompleto, usar los levels como labels
      if (length(lbls) != length(lvls)) lbls <- lvls

      factor(as.character(col_values), levels = lvls, labels = lbls)
    } else {
      # Sin configuracion: factor simple con orden alfanumerico
      factor(as.character(col_values))
    }
  }

  # Aplicar factor_config al target
  df_work[[target]] <- make_factor(df_work[[target]], target)

  # Numericas → numeric
  for (v in numeric_vars) {
    df_work[[v]] <- suppressWarnings(as.numeric(df_work[[v]]))
  }

  # Categoricas → factor con config del usuario
  for (v in categorical_vars) {
    df_work[[v]] <- make_factor(df_work[[v]], v)
  }

  # ── 5. Etiquetas de columna para gtsummary ────────────────────────────────
  # Usa el nombre de la columna como etiqueta por defecto
  label_list <- setNames(as.list(all_feature_vars), all_feature_vars)

  # ── 6. Generar tbl_summary ────────────────────────────────────────────────
  tbl <- tryCatch({
    gtsummary::tbl_summary(
      data      = df_work,
      by        = target,
      include   = all_of(all_feature_vars),
      label     = label_list,
      missing   = "ifany",
      statistic = list(
        all_continuous()  ~ "{median} [{p25}, {p75}]",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous()  ~ 2,
        all_categorical() ~ c(0, 1)
      )
    ) |>
      gtsummary::add_overall() |>
      gtsummary::add_n() |>
      gtsummary::add_p() |>
      gtsummary::bold_labels() |>
      gtsummary::modify_caption(
        paste0("**Tabla descriptiva estratificada por: ", target, "**")
      ) |>
      gtsummary::modify_header(
        label ~ "**Variable**",
        all_stat_cols() ~ "**{level}** (N={n})"
      )
  }, error = function(e) {
    return(list(error_msg = conditionMessage(e)))
  })

  if (!is.null(tbl$error_msg)) {
    res$status <- 500
    return(list(error = paste("Error al generar tbl_summary:", tbl$error_msg)))
  }

  # ── 7. Convertir a HTML ───────────────────────────────────────────────────
  html_table <- tryCatch({
    gt_tbl   <- gtsummary::as_gt(tbl)
    raw_html <- gt::as_raw_html(gt_tbl, inline_css = TRUE)
    raw_html <- iconv(raw_html, from = "UTF-8", to = "UTF-8", sub = " ")
    raw_html <- gsub("\\\\n", "\n", raw_html, fixed = TRUE)
    raw_html <- gsub("\u00a0", " ", raw_html, fixed = TRUE)
    raw_html
  }, error = function(e) NULL)

  if (is.null(html_table)) {
    res$status <- 500
    return(list(error = "No se pudo convertir la tabla a HTML."))
  }

  # ── 8. Respuesta ──────────────────────────────────────────────────────────
  return(list(
    html   = jsonlite::unbox(html_table),
    status = jsonlite::unbox("ok"),
    n_rows = jsonlite::unbox(nrow(df_work)),
    target = jsonlite::unbox(target),
    vars   = list(
      numeric     = numeric_vars,
      categorical = categorical_vars
    )
  ))
}

# ─────────────────────────────────────────────────────────────────────────────
# Health-check
# ─────────────────────────────────────────────────────────────────────────────
#* @get /health
#* @serializer json
function() {
  list(
    status    = jsonlite::unbox("ok"),
    timestamp = jsonlite::unbox(format(Sys.time(), "%Y-%m-%d %H:%M:%S")),
    packages  = list(
      plumber   = jsonlite::unbox(as.character(packageVersion("plumber"))),
      gtsummary = jsonlite::unbox(as.character(packageVersion("gtsummary"))),
      gt        = jsonlite::unbox(as.character(packageVersion("gt")))
    )
  )
}
