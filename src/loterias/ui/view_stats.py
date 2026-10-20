"""Vista de Estadística: frecuencias, número caliente, mapa de calor y atrasos.

Lee de la DB local (offline) y ofrece un botón para sincronizar los resultados
nuevos cuando hay internet. Los gráficos se dibujan con contenedores (sin
dependencias extra de charts).
"""

from __future__ import annotations

from datetime import date, timedelta

import flet as ft

from loterias import config
from loterias.core import stats
from loterias.data import db, repository, sync

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
ALTURA_BARRA = 120
CELDA = 38          # tamaño de celda del heatmap
ANCHO_ETQ = 40      # ancho de la columna de etiquetas

# Presets de rango: etiqueta -> días hacia atrás (None = todo el histórico).
RANGOS: dict[str, int | None] = {"30": 30, "90": 90, "365": 365, "todo": None}


def _metrica(titulo: str, valor: str) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=12,
        border_radius=12,
        bgcolor=ft.Colors.SECONDARY_CONTAINER,
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text(titulo, size=12, color=ft.Colors.ON_SECONDARY_CONTAINER),
                ft.Text(valor, size=22, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SECONDARY_CONTAINER),
            ],
        ),
    )


def _barras(conteos: list[int]) -> ft.Control:
    maximo = max(conteos) or 1
    columnas = []
    for digito, c in enumerate(conteos):
        alto = 4 + (c / maximo) * ALTURA_BARRA
        columnas.append(
            ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(str(c), size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(width=22, height=alto, border_radius=4,
                                 bgcolor=ft.Colors.PRIMARY),
                    ft.Text(str(digito), size=12, weight=ft.FontWeight.BOLD),
                ],
            )
        )
    fila = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                  vertical_alignment=ft.CrossAxisAlignment.END, controls=columnas)
    # Scroll horizontal por si no caben en pantallas angostas.
    return ft.Row([fila], scroll=ft.ScrollMode.AUTO, tight=True)


def _celda(valor: int, maximo: int, color) -> ft.Container:
    intensidad = (valor / maximo) if maximo else 0
    return ft.Container(
        width=CELDA, height=CELDA, border_radius=6,
        bgcolor=ft.Colors.with_opacity(0.12 + 0.88 * intensidad, color) if valor else
        ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
        alignment=ft.Alignment.CENTER,
        content=ft.Text(str(valor), size=12,
                        color=ft.Colors.ON_SURFACE if intensidad < 0.6 else ft.Colors.SURFACE),
    )


def _grilla(matriz: list[list[int]], etiquetas_fila: list[str], color) -> ft.Control:
    maximo = max((v for fila in matriz for v in fila), default=0)
    encabezado = ft.Row(
        spacing=5,
        controls=[ft.Container(width=ANCHO_ETQ, height=20)]
        + [ft.Container(width=CELDA, alignment=ft.Alignment.CENTER,
                        content=ft.Text(str(d), size=12, weight=ft.FontWeight.BOLD))
           for d in range(10)],
    )
    filas = [encabezado]
    for etiqueta, valores in zip(etiquetas_fila, matriz):
        filas.append(
            ft.Row(
                spacing=5,
                controls=[ft.Container(width=ANCHO_ETQ, alignment=ft.Alignment.CENTER_LEFT,
                                       content=ft.Text(etiqueta, size=12))]
                + [_celda(v, maximo, color) for v in valores],
            )
        )
    grid = ft.Column(spacing=5, controls=filas, tight=True)
    # Scroll horizontal: en móvil las 10 columnas no caben a lo ancho.
    return ft.Row([grid], scroll=ft.ScrollMode.AUTO, tight=True)


class VistaStats:
    """Encapsula la vista de estadística y su recarga desde la DB."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.slug = next(iter(config.LOTERIAS))
        self.dias: int | None = 30   # None = todo el histórico
        self.posicion = 0

        self._metricas = ft.Row(spacing=10)
        self._freq = ft.Container()
        self._calor = ft.Container()
        self._atrasos = ft.Container()
        self._estado = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT)

        self.control = self._construir()
        self.cargar(update=False)

    # ---- construcción de la UI (una sola vez) ----
    def _construir(self) -> ft.Control:
        dd = ft.Dropdown(
            value=self.slug,
            options=[ft.DropdownOption(key=s, text=n) for s, n in config.LOTERIAS.items()],
            on_select=self._on_loteria,
            expand=True,
        )
        rango = ft.SegmentedButton(
            selected=["30"],
            allow_multiple_selection=False,
            segments=[
                ft.Segment(value="30", label=ft.Text("30 d")),
                ft.Segment(value="90", label=ft.Text("90 d")),
                ft.Segment(value="365", label=ft.Text("1 año")),
                ft.Segment(value="todo", label=ft.Text("Todo")),
            ],
            on_change=self._on_rango,
        )
        cifras = ft.SegmentedButton(
            selected=["0"],
            allow_multiple_selection=False,
            segments=[ft.Segment(value=str(i), label=ft.Text(f"Cifra {i+1}"))
                      for i in range(stats.N_POSICIONES)],
            on_change=self._on_cifra,
        )
        btn = ft.Button("Sincronizar", icon=ft.Icons.REFRESH, on_click=self._on_sync)

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Row([ft.Icon(ft.Icons.BAR_CHART),
                        ft.Text("Estadística", size=22, weight=ft.FontWeight.BOLD)]),
                dd,
                rango,
                ft.Row([btn, self._estado]),
                self._metricas,
                ft.Text("Frecuencia por dígito", weight=ft.FontWeight.BOLD),
                cifras,
                self._freq,
                ft.Text("Mapa de calor: día de semana × dígito", weight=ft.FontWeight.BOLD),
                self._calor,
                ft.Text("Atrasos (sorteos desde la última aparición)",
                        weight=ft.FontWeight.BOLD),
                self._atrasos,
            ],
        )

    # ---- carga / recálculo ----
    def cargar(self, update: bool = True) -> None:
        con = db.conectar()
        try:
            filas = repository.obtener(con, slug=self.slug)
        finally:
            con.close()
        regs = stats.preparar(filas)
        if regs and self.dias is not None:
            limite = max(r.fecha for r in regs) - timedelta(days=self.dias)
            regs = [r for r in regs if r.fecha >= limite]

        self._render(regs)
        if update:
            self._actualizar()

    def _render(self, regs: list[stats.Registro]) -> None:
        caliente = stats.numero_caliente(regs) or "—"
        prom = stats.suma_promedio(regs)
        self._metricas.controls = [
            _metrica("Sorteos", str(len(regs))),
            _metrica("Nº caliente", caliente),
            _metrica("Suma prom.", f"{prom:.1f}" if prom is not None else "—"),
        ]

        if regs:
            freqs = stats.frecuencias_por_posicion(regs)
            self._freq.content = _barras(freqs[self.posicion])
            self._calor.content = _grilla(
                stats.matriz_dia_digito(regs, self.posicion), DIAS_SEMANA, ft.Colors.BLUE)
            etq_pos = [f"Cifra {i+1}" for i in range(stats.N_POSICIONES)]
            self._atrasos.content = _grilla(stats.atrasos(regs), etq_pos, ft.Colors.RED)
        else:
            vacio = ft.Text("Sin datos para este filtro.", color=ft.Colors.ON_SURFACE_VARIANT)
            self._freq.content = vacio
            self._calor.content = ft.Text("")
            self._atrasos.content = ft.Text("")

    def _actualizar(self) -> None:
        try:
            self.page.update()
        except Exception:
            pass

    # ---- eventos ----
    def _on_loteria(self, e: ft.Event[ft.Dropdown]) -> None:
        self.slug = e.control.value
        self.cargar()

    def _on_rango(self, e: ft.Event[ft.SegmentedButton]) -> None:
        seleccion = e.control.selected
        if seleccion:
            self.dias = RANGOS[seleccion[0]]
            self.cargar()

    def _on_cifra(self, e: ft.Event[ft.SegmentedButton]) -> None:
        seleccion = e.control.selected
        if seleccion:
            self.posicion = int(seleccion[0])
            self.cargar()

    def _on_sync(self, e) -> None:
        self._estado.value = "Sincronizando…"
        self._actualizar()
        self.page.run_thread(self._tarea_sync)

    def _tarea_sync(self) -> None:
        con = db.conectar()
        try:
            res = sync.sincronizar(con)
        finally:
            con.close()
        if res.error:
            self._estado.value = "Sin conexión: mostrando datos guardados."
        else:
            self._estado.value = f"Actualizado: +{res.insertados} resultados nuevos."
        self.cargar()
