"""Punto de entrada de la app Flet (Cruz de la suerte + Estadística).

Ejecutar en desarrollo desde la raíz del proyecto:
    pipenv run flet run loterias/main.py
o:
    pipenv run python -m loterias.main
"""

from __future__ import annotations

import flet as ft

from loterias.ui.view_cruz import crear_vista_cruz


def _vista_stats_placeholder() -> ft.Control:
    return ft.Container(
        padding=20,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.INSIGHTS, size=48, color=ft.Colors.OUTLINE),
                ft.Text("Estadística", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Próximamente: datos y análisis.",
                        color=ft.Colors.ON_SURFACE_VARIANT),
            ],
        ),
    )


def main(page: ft.Page) -> None:
    page.title = "Cruz de la suerte"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

    contenido = ft.Container(expand=True)
    vistas = [crear_vista_cruz(page), _vista_stats_placeholder()]
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


if __name__ == "__main__":
    ft.run(main)
