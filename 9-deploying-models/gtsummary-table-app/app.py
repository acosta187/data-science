"""
Streamlit App — Tabla descriptiva con gtsummary (via Plumber API en R)
Interfaz rediseñada: wizard paso a paso, visual limpio y amigable.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

# ── Configuracion de pagina ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Tabla Descriptiva · gtsummary",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fondo general */
.stApp {
    background: #f7f8fc;
}

/* Oculta header por defecto */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a1d2e;
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #a0a8c0 !important;
    font-size: 0.85rem;
}

/* Titulo principal */
.main-title {
    font-size: 2rem;
    font-weight: 600;
    color: #1a1d2e;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
.main-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* Step badges */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #1a1d2e;
    color: white;
    border-radius: 20px;
    padding: 4px 14px 4px 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}
.step-num {
    background: #4f6ef7;
    color: white;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
}
.step-done {
    background: #d1fae5;
    color: #065f46;
}
.step-done .step-num {
    background: #10b981;
}

/* Cards */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* Stat chips */
.stat-chip {
    display: inline-block;
    background: #f0f4ff;
    color: #3b4fd8;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 500;
    font-family: 'DM Mono', monospace;
    margin-right: 6px;
}

/* Botón principal */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.65rem 2rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(79, 110, 247, 0.35);
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(79, 110, 247, 0.45);
}

/* Expander */
div[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    background: white;
    margin-bottom: 8px;
}

/* Tags de variables seleccionadas */
.var-tag {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 2px;
    font-family: 'DM Mono', monospace;
}
.var-tag.cat {
    background: #fdf4ff;
    color: #7e22ce;
    border-color: #e9d5ff;
}
.var-tag.target {
    background: #fff7ed;
    color: #c2410c;
    border-color: #fed7aa;
}

/* Alerta de éxito personalizada */
.success-banner {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    border: 1px solid #6ee7b7;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #065f46;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* Separador */
hr { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }

/* Inputs */
.stTextInput input, .stSelectbox select {
    border-radius: 8px !important;
}

/* Number input compacto */
.stNumberInput input {
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace;
    text-align: center;
}

/* Info box */
.info-box {
    background: #eff6ff;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    color: #1e40af;
    font-size: 0.88rem;
}

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #9ca3af;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h3 { color: #6b7280; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

DEFAULT_API_URL = "http://localhost:8000/tbl_summary"


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Formato no soportado. Usa .csv o .xlsx")


def validate_binary_target(df: pd.DataFrame, target: str) -> bool:
    return df[target].dropna().nunique() == 2


def clean_html(raw) -> str:
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    return (
        str(raw)
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\xa0", " ")
        .replace("\xa0", " ")
    )


def send_to_api(payload: dict, api_url: str) -> dict:
    response = requests.post(
        api_url,
        json=payload,
        timeout=60,
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def step_badge(num, label, done=False):
    cls = "step-badge step-done" if done else "step-badge"
    icon = "✓" if done else num
    return f'<div class="{cls}"><span class="step-num">{icon}</span>{label}</div>'


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")
    api_url = st.text_input(
        "URL del API Plumber",
        value=DEFAULT_API_URL,
        help="Endpoint del servicio R backend.",
    )
    if not api_url:
        api_url = DEFAULT_API_URL

    st.markdown("---")
    st.markdown("**Cómo funciona**")
    st.markdown("""
1. Sube tu dataset
2. Define la variable objetivo
3. Selecciona variables
4. Configura etiquetas
5. Genera la tabla
    """)
    st.markdown("---")
    st.markdown("**Stack**")
    st.markdown("Frontend · `Streamlit`\nBackend · `Plumber + R`\nTablas · `gtsummary`")


# ── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">📊 Tabla Descriptiva</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Genera tablas descriptivas estratificadas con <strong>gtsummary</strong> · Sigue los pasos a continuación</p>', unsafe_allow_html=True)

# Progreso visual
df = None
target = None
numeric_vars = []
categorical_vars = []

# ════════════════════════════════════════════════════════════════════════════
# PASO 1 — Dataset
# ════════════════════════════════════════════════════════════════════════════
step1_done = False

with st.container():
    st.markdown(step_badge(1, "Cargar dataset"), unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Arrastra o selecciona un archivo",
        type=["xlsx", "csv"],
        label_visibility="collapsed",
        help="Formatos soportados: .xlsx y .csv",
    )

if uploaded is not None:
    try:
        df = load_file(uploaded)
        step1_done = True

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Filas", f"{df.shape[0]:,}")
        col_b.metric("Columnas", f"{df.shape[1]}")
        col_c.metric("Archivo", uploaded.name.split(".")[-1].upper())
        col_d.metric("Peso aprox.", f"{uploaded.size / 1024:.1f} KB")

        with st.expander("👁️ Vista previa del dataset"):
            st.dataframe(df.head(15), use_container_width=True, height=280)

    except Exception as e:
        st.error(f"❌ No se pudo cargar el archivo: {e}")
        st.stop()
else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📁</div>
        <h3>Sin dataset cargado</h3>
        <p>Sube un archivo <code>.xlsx</code> o <code>.csv</code> para comenzar</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PASO 2 — Variables
# ════════════════════════════════════════════════════════════════════════════
all_cols = df.columns.tolist()

st.markdown(step_badge(2, "Seleccionar variables", done=step1_done), unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    target = st.selectbox(
        "🎯 Variable objetivo (target binaria)",
        options=["— Seleccionar —"] + all_cols,
    )
    if target != "— Seleccionar —":
        vals = sorted([str(v) for v in df[target].dropna().unique()])
        is_binary = len(vals) == 2
        if is_binary:
            st.markdown(
                f'<div class="info-box">✅ Variable binaria detectada · '
                f'<span class="stat-chip">{vals[0]}</span>'
                f'<span class="stat-chip">{vals[1]}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.error(f"⚠️ No es binaria ({len(vals)} valores únicos). Elige otra variable.")
            target = "— Seleccionar —"

with col2:
    remaining = [c for c in all_cols if c != target]
    numeric_vars = st.multiselect(
        "🔢 Variables numéricas",
        options=remaining,
        placeholder="Selecciona una o más...",
    )

cat_options = [c for c in remaining if c not in numeric_vars]
categorical_vars = st.multiselect(
    "🏷️ Variables categóricas",
    options=cat_options,
    placeholder="Selecciona una o más...",
)

# Resumen visual de selección
if target != "— Seleccionar —" or numeric_vars or categorical_vars:
    tags_html = ""
    if target != "— Seleccionar —":
        tags_html += f'<span class="var-tag target">🎯 {target}</span>'
    for v in numeric_vars:
        tags_html += f'<span class="var-tag">{v}</span>'
    for v in categorical_vars:
        tags_html += f'<span class="var-tag cat">{v}</span>'
    st.markdown(f"<div style='margin-top:0.5rem'>{tags_html}</div>", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PASO 3 — Configurar factores
# ════════════════════════════════════════════════════════════════════════════
cat_vars_to_configure = []
if target != "— Seleccionar —":
    cat_vars_to_configure.append(("target", target))
for v in categorical_vars:
    cat_vars_to_configure.append(("cat", v))

factor_config = {}

if cat_vars_to_configure:
    vars_ready = target != "— Seleccionar —" or categorical_vars
    st.markdown(step_badge(3, "Configurar niveles y etiquetas", done=False), unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box" style="margin-bottom:1rem">Asigna un <strong>orden</strong> (posición) y una <strong>etiqueta legible</strong> para cada nivel. '
        'El nivel en posición 1 será la referencia en gtsummary.</div>',
        unsafe_allow_html=True,
    )

    for kind, varname in cat_vars_to_configure:
        raw_levels = sorted([str(v) for v in df[varname].dropna().unique()])
        n_levels = len(raw_levels)
        icon = "🎯" if kind == "target" else "🏷️"
        badge_txt = "Target" if kind == "target" else "Categórica"

        with st.expander(f"{icon} **{varname}** · {badge_txt} · {n_levels} niveles", expanded=True):
            header_cols = st.columns([1, 3, 5])
            header_cols[0].markdown("**Posición**")
            header_cols[1].markdown("**Valor original**")
            header_cols[2].markdown("**Etiqueta**")

            level_configs = []
            for i, lvl in enumerate(raw_levels):
                c1, c2, c3 = st.columns([1, 3, 5])
                with c1:
                    pos = st.number_input(
                        "pos",
                        min_value=1,
                        max_value=n_levels,
                        value=i + 1,
                        step=1,
                        key=f"pos_{varname}_{i}",
                        label_visibility="collapsed",
                    )
                with c2:
                    st.markdown(f"<code style='font-size:0.9rem'>{lvl}</code>", unsafe_allow_html=True)
                with c3:
                    label = st.text_input(
                        "etiqueta",
                        value=lvl,
                        key=f"lbl_{varname}_{i}",
                        label_visibility="collapsed",
                        placeholder=f"Etiqueta para '{lvl}'",
                    )
                level_configs.append((pos, lvl, label))

            sorted_configs = sorted(level_configs, key=lambda x: x[0])
            ordered_levels = [x[1] for x in sorted_configs]
            ordered_labels = [x[2] for x in sorted_configs]

            prev_df = pd.DataFrame({
                "Pos.": range(1, len(ordered_levels) + 1),
                "Valor": ordered_levels,
                "Etiqueta": ordered_labels,
            })
            st.caption("Vista previa del orden final:")
            st.dataframe(prev_df, use_container_width=True, hide_index=True, height=120)

            factor_config[varname] = {
                "levels": ordered_levels,
                "labels": ordered_labels,
            }

    st.markdown("---")
    section_num = 4
else:
    section_num = 3

# ════════════════════════════════════════════════════════════════════════════
# PASO N — Generar tabla
# ════════════════════════════════════════════════════════════════════════════
st.markdown(step_badge(section_num, "Generar tabla descriptiva"), unsafe_allow_html=True)

# Checklist rápida antes del botón
checks = {
    "Dataset cargado": df is not None,
    "Variable objetivo seleccionada": target != "— Seleccionar —",
    "Al menos una variable seleccionada": bool(numeric_vars or categorical_vars),
}
all_ok = all(checks.values())

check_cols = st.columns(len(checks))
for col, (label, ok) in zip(check_cols, checks.items()):
    icon = "✅" if ok else "⬜"
    col.markdown(f"{icon} {label}")

st.write("")

generate_btn = st.button(
    "⚡ Generar tabla con gtsummary",
    type="primary",
    use_container_width=True,
    disabled=not all_ok,
)

if not all_ok:
    st.markdown(
        '<div class="info-box" style="margin-top:0.5rem">Completa los pasos anteriores para habilitar la generación.</div>',
        unsafe_allow_html=True,
    )

if generate_btn:
    cols = list({target} | set(numeric_vars) | set(categorical_vars))
    payload = {
        "data": df[cols].to_json(orient="records"),
        "target": target,
        "numeric_vars": numeric_vars,
        "categorical_vars": categorical_vars,
        "factor_config": factor_config,
    }

    with st.spinner("Conectando con el backend R · generando tabla..."):
        try:
            result = send_to_api(payload, api_url)
        except requests.exceptions.ConnectionError:
            st.error(
                f"❌ No se pudo conectar al API en `{api_url}`. "
                "Verifica que el servidor R (Plumber) esté corriendo."
            )
            st.stop()
        except requests.exceptions.Timeout:
            st.error("⏱️ El API tardó demasiado en responder (timeout: 60 s).")
            st.stop()
        except requests.exceptions.HTTPError as e:
            try:
                msg = e.response.json().get("error", str(e))
            except Exception:
                msg = str(e)
            st.error(f"❌ Error del API ({e.response.status_code}): {msg}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")
            st.stop()

    if "error" in result:
        st.error(f"El API reportó un error: {result['error']}")

    elif "html" in result:
        html_clean = clean_html(result["html"])

        st.markdown(
            '<div class="success-banner">✅ Tabla generada correctamente</div>',
            unsafe_allow_html=True,
        )

        st.subheader("Resultado · Tabla descriptiva")

        full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'DM Sans', Arial, sans-serif; font-size: 14px; margin: 0; padding: 12px; background: #fff; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th {{ background: #1a1d2e; color: white; padding: 8px 12px; text-align: left; font-weight: 500; }}
    td {{ padding: 7px 12px; border-bottom: 1px solid #f0f0f0; }}
    tr:hover td {{ background: #f8faff; }}
  </style>
</head>
<body>{html_clean}</body>
</html>"""

        components.html(full_html, height=650, scrolling=True)

        st.download_button(
            label="⬇️ Descargar tabla como HTML",
            data=html_clean.encode("utf-8"),
            file_name="tabla_descriptiva.html",
            mime="text/html",
        )
    else:
        st.warning("El API respondió sin HTML esperado.")
        st.json(result)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📊 Tabla Descriptiva · Frontend: Streamlit (Python) · Backend: Plumber + gtsummary (R)")
