"""Punto de entrada de la app Flet (Cruz de la suerte + Estadística).

Ejecutar en desarrollo desde la raíz del proyecto:
    pipenv run python -m loterias.main
"""

from __future__ import annotations

import flet as ft

from loterias.data import db, sync
from loterias.ui.view_cruz import crear_vista_cruz
from loterias.ui.view_stats import VistaStats


def main(page: ft.Page) -> None:
    page.title = "Cruz de la suerte"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

    vista_stats = VistaStats(page)
    contenido = ft.Container(expand=True)
    vistas = [crear_vista_cruz(page), vista_stats.control]
    contenido.content = vistas[0]

    def cambiar_vista(e: ft.Event[ft.NavigationBar]) -> None:
        contenido.content = vistas[e.control.selected_index]

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=cambiar_vista,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CASINO, label="Cruz"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Estadística"),
        ],
    )
    page.add(ft.SafeArea(expand=True, content=contenido))

    # Sync incremental al arranque, en segundo plano (no bloquea la UI).
    def _sync_inicial() -> None:
        con = db.conectar()
        try:
            sync.sincronizar(con)
        finally:
            con.close()
        vista_stats.cargar()

    page.run_thread(_sync_inicial)


if __name__ == "__main__":
    ft.run(main)
