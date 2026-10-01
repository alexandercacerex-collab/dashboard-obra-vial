"""Genera la base sintética utilizada por el dashboard."""

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
rng = np.random.default_rng(20260930)

fechas = pd.date_range("2026-01-01", "2026-09-30", freq="D")

partidas = {
    "Desbroce y limpieza": ("m2", 1800, 2.80),
    "Excavación material suelto": ("m3", 950, 9.50),
    "Excavación roca fija": ("m3", 420, 28.00),
    "Subbase granular": ("m3", 520, 32.00),
    "Base granular": ("m3", 460, 38.00),
    "Pavimento asfáltico": ("t", 310, 185.00),
    "Cunetas de concreto": ("m", 115, 145.00),
}

frentes = ["Frente 01", "Frente 02", "Frente 03"]
equipos = [
    "Excavadora",
    "Cargador frontal",
    "Motoniveladora",
    "Rodillo",
    "Volquete",
    "Pavimentadora",
]

registros = []
correlativo = 1

for fecha in fechas:
    actividades = rng.choice(
        list(partidas.keys()),
        size=int(rng.integers(2, 5)),
        replace=False,
    )

    for partida in actividades:
        unidad, rendimiento_base, costo_unitario = partidas[partida]

        programado = rendimiento_base * np.clip(
            rng.normal(1.0, 0.05), 0.88, 1.12
        )
        factor = np.clip(rng.normal(0.91, 0.14), 0.50, 1.20)
        real = programado * factor

        registros.append({
            "id_registro": f"OV-{correlativo:05d}",
            "fecha": fecha.strftime("%Y-%m-%d"),
            "frente": rng.choice(frentes),
            "partida": partida,
            "unidad": unidad,
            "equipo_principal": rng.choice(equipos),
            "personal": int(rng.integers(4, 10)),
            "produccion_programada": round(programado, 2),
            "produccion_real": round(real, 2),
            "cumplimiento_pct": round(real / programado * 100, 2),
            "horas_equipo": round(float(np.clip(rng.normal(9.2, 1.2), 5, 12)), 2),
            "horas_parada": round(float(np.clip(rng.normal(0.7, 0.55), 0, 4.5)), 2),
            "costo_programado_soles": round(programado * costo_unitario, 2),
            "costo_real_soles": round(real * costo_unitario * rng.uniform(1.00, 1.10), 2),
            "incidencia": rng.choice(
                [
                    "Sin incidencia",
                    "Falla mecánica",
                    "Espera de topografía",
                    "Clima",
                    "Cambio de frente",
                    "Abastecimiento de material",
                ],
                p=[0.62, 0.08, 0.07, 0.06, 0.08, 0.09],
            ),
            "control_calidad": rng.choice(
                ["Conforme", "Observado"],
                p=[0.94, 0.06],
            ),
        })

        correlativo += 1

df = pd.DataFrame(registros)

df.to_csv(
    BASE_DIR / "base_obra_vial_ia.csv",
    index=False,
    encoding="utf-8-sig",
)

with sqlite3.connect(BASE_DIR / "base_obra_vial_ia.sqlite") as con:
    df.to_sql("avance_obra", con, if_exists="replace", index=False)

print(f"Base generada correctamente: {len(df)} registros")
