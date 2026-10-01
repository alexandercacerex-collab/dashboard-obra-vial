from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard de Obra Vial", page_icon="🏗️", layout="wide")
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "base_obra_vial_ia.csv"

@st.cache_data
def cargar_datos():
    if not DATA_FILE.exists():
        st.error("No se encontró base_obra_vial_ia.csv en la misma carpeta que app.py")
        st.stop()
    data = pd.read_csv(DATA_FILE)
    data["fecha"] = pd.to_datetime(data["fecha"], errors="coerce")
    return data.dropna(subset=["fecha"]).copy()

df = cargar_datos()
st.title("🏗️ Dashboard de Control de Avance de Obra Vial")
st.caption("Entrega final de Python | Base sintética generada con apoyo de IA")
st.sidebar.header("Filtros")
fecha_min, fecha_max = df["fecha"].min().date(), df["fecha"].max().date()
rango = st.sidebar.date_input("Rango de fechas", value=(fecha_min, fecha_max), min_value=fecha_min, max_value=fecha_max)
frentes_disp = sorted(df["frente"].dropna().unique().tolist())
partidas_disp = sorted(df["partida"].dropna().unique().tolist())
frentes = st.sidebar.multiselect("Frente de trabajo", frentes_disp, default=frentes_disp)
partidas = st.sidebar.multiselect("Partida", partidas_disp, default=partidas_disp)
f = df.copy()
if isinstance(rango,(list,tuple)) and len(rango)==2:
    ini, fin = pd.to_datetime(rango[0]), pd.to_datetime(rango[1])
    f = f[(f["fecha"]>=ini)&(f["fecha"]<=fin)]
f = f[f["frente"].isin(frentes) & f["partida"].isin(partidas)]
if f.empty:
    st.warning("No existen registros con los filtros seleccionados.")
    st.stop()
prog=f["produccion_programada"].sum(); real=f["produccion_real"].sum(); cump=(real/prog*100) if prog else 0
cp=f["costo_programado_soles"].sum(); cr=f["costo_real_soles"].sum(); desv=cr-cp; hp=f["horas_parada"].sum()
c1,c2,c3,c4,c5=st.columns(5)
c1.metric("Producción programada",f"{prog:,.0f}")
c2.metric("Producción real",f"{real:,.0f}")
c3.metric("Cumplimiento",f"{cump:.1f}%")
c4.metric("Desviación de costo",f"S/ {desv:,.0f}")
c5.metric("Horas de parada",f"{hp:,.1f} h")
st.divider()
diario=f.groupby("fecha",as_index=False).agg(programado=("produccion_programada","sum"),real=("produccion_real","sum")).sort_values("fecha")
diario["programado_acumulado"]=diario["programado"].cumsum(); diario["real_acumulado"]=diario["real"].cumsum()
curva=diario.melt(id_vars="fecha",value_vars=["programado_acumulado","real_acumulado"],var_name="serie",value_name="produccion")
curva["serie"]=curva["serie"].replace({"programado_acumulado":"Programado acumulado","real_acumulado":"Real acumulado"})
st.plotly_chart(px.line(curva,x="fecha",y="produccion",color="serie",title="Curva S simplificada: producción acumulada"),use_container_width=True)
col1,col2=st.columns(2)
with col1:
    rend=f.groupby("partida",as_index=False).agg(cumplimiento_promedio=("cumplimiento_pct","mean")).sort_values("cumplimiento_promedio")
    st.plotly_chart(px.bar(rend,x="cumplimiento_promedio",y="partida",orientation="h",text_auto=".1f",title="Cumplimiento promedio por partida (%)"),use_container_width=True)
with col2:
    incid=f.groupby("incidencia",as_index=False).size().rename(columns={"size":"eventos"})
    st.plotly_chart(px.pie(incid,names="incidencia",values="eventos",hole=0.45,title="Distribución de incidencias"),use_container_width=True)
col3,col4=st.columns(2)
with col3:
    costos=f.groupby("frente",as_index=False).agg(costo_programado=("costo_programado_soles","sum"),costo_real=("costo_real_soles","sum")).melt(id_vars="frente",value_vars=["costo_programado","costo_real"],var_name="tipo",value_name="monto")
    costos["tipo"]=costos["tipo"].replace({"costo_programado":"Programado","costo_real":"Real"})
    st.plotly_chart(px.bar(costos,x="frente",y="monto",color="tipo",barmode="group",title="Costo programado vs. real por frente"),use_container_width=True)
with col4:
    par=f.groupby("equipo_principal",as_index=False).agg(horas_parada=("horas_parada","sum")).sort_values("horas_parada",ascending=False)
    st.plotly_chart(px.bar(par,x="equipo_principal",y="horas_parada",text_auto=".1f",title="Horas de parada por equipo"),use_container_width=True)
st.subheader("Control de calidad")
cal=f["control_calidad"].value_counts().rename_axis("estado").reset_index(name="registros")
st.dataframe(cal,use_container_width=True,hide_index=True)
st.subheader("Detalle de registros")
det=f.sort_values(["fecha","frente"],ascending=[False,True]).copy(); det["fecha"]=det["fecha"].dt.strftime("%Y-%m-%d")
st.dataframe(det,use_container_width=True,hide_index=True)
st.download_button("Descargar datos filtrados",data=det.to_csv(index=False).encode("utf-8-sig"),file_name="avance_obra_filtrado.csv",mime="text/csv")
st.caption("Fuente: base sintética generada con Python y apoyo de IA, exclusivamente para fines académicos.")
