"""Constantes de configuración de la app."""

from __future__ import annotations

# API pública de resultados (consulta por fecha: .../results/YYYY-MM-DD)
API_BASE = "https://api-resultadosloterias.com/api/results"

# Loterías que seguimos (slug de la API -> nombre para mostrar).
LOTERIAS: dict[str, str] = {
    "sinuano-dia": "Sinuano Día",
    "sinuano-noche": "Sinuano Noche",
    "caribena-dia": "Caribeña Día",
    "caribena-noche": "Caribeña Noche",
    "super-astro-sol": "Super Astro Sol",
    "super-astro-luna": "Super Astro Luna",
    "super-astro-estrella": "Super Astro Estrella",
}

# Días que se vuelven a pedir en cada sync, por si un resultado se publicó tarde.
REFETCH_DIAS = 3

# Si la DB está vacía (sin seed), cuántos días hacia atrás bajar la primera vez.
DIAS_INICIAL = 90

# Pausa entre peticiones a la API, para no saturarla.
PAUSA_PETICION_S = 1.0
