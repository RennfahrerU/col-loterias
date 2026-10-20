"""Entry point para Flet (`flet run` y `flet build`).

La lógica de la app vive en el paquete `loterias`; aquí solo se expone `main`
para que el runtime de Flet lo encuentre.
"""

from loterias.main import main

if __name__ == "__main__":
    import flet as ft

    ft.run(main)
