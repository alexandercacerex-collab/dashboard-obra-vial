# Entrega Final – Dashboard de Control de Obra Vial

## 1. Objetivo

Desarrollar un dashboard interactivo utilizando una base de datos sintética
generada con Python y apoyo de IA. El tablero permite analizar el control de
avance de una obra vial.

## 2. Archivos del proyecto

- `app.py`: aplicación principal de Streamlit.
- `base_obra_vial_ia.csv`: base de datos utilizada por el dashboard.
- `base_obra_vial_ia.sqlite`: copia de la base en SQLite.
- `generar_base.py`: script para regenerar los datos sintéticos.
- `notebook_entrega_final.ipynb`: notebook con análisis exploratorio.
- `requirements.txt`: dependencias de Python.
- `README.md`: documentación del proyecto.

## 3. Indicadores

El dashboard presenta:

- Producción programada.
- Producción real.
- Porcentaje de cumplimiento.
- Desviación de costos.
- Horas de parada.
- Curva S simplificada.
- Cumplimiento por partida.
- Incidencias.
- Costos por frente.
- Horas de parada por equipo.
- Control de calidad.
- Tabla de registros filtrados.

## 4. Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 5. GitHub

Crear un repositorio público y subir todos los archivos manteniéndolos en la raíz.

## 6. Streamlit Community Cloud

1. Iniciar sesión con GitHub.
2. Crear una nueva aplicación.
3. Elegir el repositorio.
4. Rama: `main`.
5. Main file path: `app.py`.
6. Presionar **Deploy**.
7. Compartir la URL pública terminada en `.streamlit.app`.
