from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Obra Vial",
    page_icon="🏗️",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "base_obra_vial_ia.csv"


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Carga y prepara la base local incluida en el repositorio."""
    if not DATA_FILE.exists():
        st.error(
            "No se encontró 'base_obra_vial_ia.csv'. "
            "Verifica que el CSV esté en la misma carpeta que app.py."
        )
        st.stop()

    data = pd.read_csv(DATA_FILE)
    data["fecha"] = pd.to_datetime(data["fecha"], errors="coerce")
    data = data.dropna(subset=["fecha"]).copy()
    return data


df = cargar_datos()

st.title("🏗️ Dashboard de Control de Avance de Obra Vial")
st.caption(
    "Entrega final de Python | Base de datos sintética generada con apoyo de IA"
)

# -----------------------------
# FILTROS
# -----------------------------
st.sidebar.header("Filtros")

fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()

rango_fecha = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)

frentes_disponibles = sorted(df["frente"].dropna().unique().tolist())
partidas_disponibles = sorted(df["partida"].dropna().unique().tolist())

frentes = st.sidebar.multiselect(
    "Frente de trabajo",
    options=frentes_disponibles,
    default=frentes_disponibles,
)

partidas = st.sidebar.multiselect(
    "Partida",
    options=partidas_disponibles,
    default=partidas_disponibles,
)

filtrado = df.copy()

if isinstance(rango_fecha, (list, tuple)) and len(rango_fecha) == 2:
    inicio = pd.to_datetime(rango_fecha[0])
    fin = pd.to_datetime(rango_fecha[1])
    filtrado = filtrado[
        (filtrado["fecha"] >= inicio) &
        (filtrado["fecha"] <= fin)
    ]

if frentes:
    filtrado = filtrado[filtrado["frente"].isin(frentes)]
else:
    filtrado = filtrado.iloc[0:0]

if partidas:
    filtrado = filtrado[filtrado["partida"].isin(partidas)]
else:
    filtrado = filtrado.iloc[0:0]

if filtrado.empty:
    st.warning("No existen registros con los filtros seleccionados.")
    st.stop()

# -----------------------------
# KPI
# -----------------------------
produccion_programada = filtrado["produccion_programada"].sum()
produccion_real = filtrado["produccion_real"].sum()

cumplimiento = (
    produccion_real / produccion_programada * 100
    if produccion_programada > 0
    else 0
)

costo_programado = filtrado["costo_programado_soles"].sum()
costo_real = filtrado["costo_real_soles"].sum()
desviacion_costo = costo_real - costo_programado
horas_parada = filtrado["horas_parada"].sum()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Producción programada",
    f"{produccion_programada:,.0f}",
)

k2.metric(
    "Producción real",
    f"{produccion_real:,.0f}",
)

k3.metric(
    "Cumplimiento",
    f"{cumplimiento:.1f}%",
)

k4.metric(
    "Desviación de costo",
    f"S/ {desviacion_costo:,.0f}",
)

k5.metric(
    "Horas de parada",
    f"{horas_parada:,.1f} h",
)

st.divider()

# -----------------------------
# CURVA ACUMULADA
# -----------------------------
diario = (
    filtrado.groupby("fecha", as_index=False)
    .agg(
        programado=("produccion_programada", "sum"),
        real=("produccion_real", "sum"),
        costo_programado=("costo_programado_soles", "sum"),
        costo_real=("costo_real_soles", "sum"),
    )
    .sort_values("fecha")
)

diario["programado_acumulado"] = diario["programado"].cumsum()
diario["real_acumulado"] = diario["real"].cumsum()

curva = diario.melt(
    id_vars="fecha",
    value_vars=["programado_acumulado", "real_acumulado"],
    var_name="serie",
    value_name="produccion",
)

curva["serie"] = curva["serie"].replace({
    "programado_acumulado": "Programado acumulado",
    "real_acumulado": "Real acumulado",
})

fig_curva = px.line(
    curva,
    x="fecha",
    y="produccion",
    color="serie",
    title="Curva S simplificada: producción acumulada",
    markers=False,
)
st.plotly_chart(fig_curva, use_container_width=True)

# -----------------------------
# GRÁFICOS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    rendimiento_partida = (
        filtrado.groupby("partida", as_index=False)
        .agg(cumplimiento_promedio=("cumplimiento_pct", "mean"))
        .sort_values("cumplimiento_promedio")
    )

    fig_rendimiento = px.bar(
        rendimiento_partida,
        x="cumplimiento_promedio",
        y="partida",
        orientation="h",
        text_auto=".1f",
        title="Cumplimiento promedio por partida (%)",
    )

    st.plotly_chart(fig_rendimiento, use_container_width=True)

with col2:
    incidencias = (
        filtrado.groupby("incidencia", as_index=False)
        .size()
        .rename(columns={"size": "eventos"})
    )

    fig_incidencias = px.pie(
        incidencias,
        names="incidencia",
        values="eventos",
        hole=0.45,
        title="Distribución de incidencias",
    )

    st.plotly_chart(fig_incidencias, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    costos_frente = (
        filtrado.groupby("frente", as_index=False)
        .agg(
            costo_programado=("costo_programado_soles", "sum"),
            costo_real=("costo_real_soles", "sum"),
        )
        .melt(
            id_vars="frente",
            value_vars=["costo_programado", "costo_real"],
            var_name="tipo",
            value_name="monto",
        )
    )

    costos_frente["tipo"] = costos_frente["tipo"].replace({
        "costo_programado": "Programado",
        "costo_real": "Real",
    })

    fig_costos = px.bar(
        costos_frente,
        x="frente",
        y="monto",
        color="tipo",
        barmode="group",
        title="Costo programado vs. real por frente",
    )

    st.plotly_chart(fig_costos, use_container_width=True)

with col4:
    paradas_equipo = (
        filtrado.groupby("equipo_principal", as_index=False)
        .agg(horas_parada=("horas_parada", "sum"))
        .sort_values("horas_parada", ascending=False)
    )

    fig_paradas = px.bar(
        paradas_equipo,
        x="equipo_principal",
        y="horas_parada",
        text_auto=".1f",
        title="Horas de parada por equipo",
    )

    st.plotly_chart(fig_paradas, use_container_width=True)

# -----------------------------
# CONTROL DE CALIDAD
# -----------------------------
st.subheader("Control de calidad")

calidad = (
    filtrado["control_calidad"]
    .value_counts()
    .rename_axis("estado")
    .reset_index(name="registros")
)

st.dataframe(
    calidad,
    use_container_width=True,
    hide_index=True,
)

# -----------------------------
# DETALLE
# -----------------------------
st.subheader("Detalle de registros")

mostrar = filtrado.sort_values(
    ["fecha", "frente"],
    ascending=[False, True],
).copy()

mostrar["fecha"] = mostrar["fecha"].dt.strftime("%Y-%m-%d")

st.dataframe(
    mostrar,
    use_container_width=True,
    hide_index=True,
)

csv_filtrado = mostrar.to_csv(
    index=False,
).encode("utf-8-sig")

st.download_button(
    label="Descargar datos filtrados en CSV",
    data=csv_filtrado,
    file_name="avance_obra_filtrado.csv",
    mime="text/csv",
)

st.caption(
    "Fuente: base de datos sintética generada con Python y apoyo de IA, "
    "exclusivamente para fines académicos."
)
