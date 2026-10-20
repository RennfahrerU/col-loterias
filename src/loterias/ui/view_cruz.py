"""Vista "Cruz de la suerte": elegir una fecha y ver las 8 sumas en cruz.

El usuario elige una fecha en el calendario; la fecha se descompone en 6 dígitos
(dd mm aa) y se muestran las 8 raíces digitales dispuestas en forma de cruz.
Funciona totalmente offline.
"""

from __future__ import annotations

from datetime import date, datetime

import flet as ft

from loterias.core.cruz import ResultadoCruz, calcular_cruz, digitos_desde_fecha


def _nodo(res: ResultadoCruz) -> ft.Container:
    """Un círculo con la raíz digital grande y la operación que la origina."""
    return ft.Container(
        width=78,
        height=78,
        border_radius=39,
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(str(res.raiz), size=30, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY_CONTAINER),
                ft.Text(f"{res.izq}+{res.der}", size=11,
                        color=ft.Colors.ON_PRIMARY_CONTAINER),
            ],
        ),
    )


def _cruz(resultados: list[ResultadoCruz]) -> ft.Control:
    """Dispone los 8 nodos en forma de diamante/cruz alrededor de un centro."""
    r = {res.etiqueta: res for res in resultados}

    def fila(etqs: list[str]) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=24,
            controls=[_nodo(r[e]) for e in etqs],
        )

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        controls=[
            fila(["r", "s"]),
            fila(["t", "u"]),
            ft.Icon(ft.Icons.ADD, size=34, color=ft.Colors.OUTLINE),
            fila(["v", "x"]),
            fila(["y", "z"]),
        ],
    )


def crear_vista_cruz(page: ft.Page) -> ft.Control:
    """Construye la vista de la cruz y devuelve su control raíz."""
    fecha_sel = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    contenedor = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def mostrar(fecha: date) -> None:
        fecha_sel.value = fecha.strftime("%d/%m/%Y")
        resultados = calcular_cruz(digitos_desde_fecha(fecha))
        contenedor.controls = [_cruz(resultados)]

    def on_cambio_fecha(e: ft.Event[ft.DatePicker]) -> None:
        valor = e.control.value
        if isinstance(valor, datetime):
            valor = valor.date()
        if valor is not None:
            mostrar(valor)

    def abrir_calendario(e) -> None:
        page.show_dialog(
            ft.DatePicker(
                first_date=date(2000, 1, 1),
                last_date=date(2100, 12, 31),
                current_date=date.today(),
                on_change=on_cambio_fecha,
            )
        )

    mostrar(date.today())

    return ft.Container(
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Text("Cruz de la suerte", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_MONTH),
                        fecha_sel,
                        ft.Button("Cambiar fecha", icon=ft.Icons.EDIT_CALENDAR,
                                  on_click=abrir_calendario),
                    ],
                ),
                contenedor,
            ],
        ),
    )
