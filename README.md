# Cruz de la suerte

App de escritorio y Android (Python + [Flet](https://flet.dev)) con dos secciones:

- **Cruz de la suerte**: a partir de una fecha calcula 8 sumas cruzadas y su raíz
  digital, dispuestas en forma de X. Funciona offline.
- **Estadística**: frecuencias por cifra, número caliente, suma promedio, mapa de
  calor por día de semana y atrasos, sobre resultados de loterías colombianas
  (Sinuano, Caribeña, Super Astro). Los datos se guardan en SQLite local y se
  sincronizan de forma incremental cuando hay internet.

## Requisitos

- Python 3.13 y **Pipenv** (obligatorio para el entorno de desarrollo).
- Para compilar el APK: JDK 17, Android SDK y Modo de desarrollador de Windows
  (ver más abajo). Flet 1.0 gestiona su propia copia de Flutter.

## Desarrollo

```bash
pipenv install
pipenv run flet run        # app con hot reload (escritorio)
```

Fuera de Flet también corre con `PYTHONPATH=src pipenv run python -m loterias.main`.

### Estructura

```
src/
  main.py                 # entry para flet run / flet build
  loterias/
    main.py               # shell: navegación Cruz / Estadística
    config.py             # loterías objetivo, API, parámetros de sync
    core/                 # lógica pura (sin UI ni I/O), testeable
      cruz.py             # raíz digital + 8 sumas cruzadas
      stats.py            # frecuencias, número caliente, atrasos...
    data/
      db.py               # SQLite: esquema, ruta por plataforma, copia del seed
      repository.py       # consultas / inserciones
      sync.py             # scraper incremental
      seed.db             # histórico inicial (se empaqueta con la app)
    ui/
      view_cruz.py
      view_stats.py
scripts/
  migrar_seed.py          # regenera seed.db desde data_loterias_completo.csv
pyproject.toml            # metadatos y config de flet build (NO gestiona el entorno)
Pipfile                   # entorno de desarrollo (Pipenv)
```

## Datos y sincronización

- Una tabla `resultados (slug, date, lottery, result, series)` con clave primaria
  `(slug, date)`: deduplica por lotería y día.
- La DB vive en `FLET_APP_STORAGE_DATA` (persistente en Android/escritorio). En
  desarrollo fuera de Flet se usa `.data/` en la raíz.
- Al abrir con internet, el sync baja solo los días nuevos desde la última fecha
  menos una ventana de re-fetch de 3 días (por resultados publicados tarde). Sin
  internet, la app usa lo ya guardado.
- `pipenv run python scripts/migrar_seed.py` regenera `seed.db` desde el CSV.

## Empaquetar el APK

Prerrequisitos (una sola vez):

1. **JDK 17** y `JAVA_HOME` apuntando a él.
2. **Android SDK** (cmdline-tools) con: `platform-tools`, `platforms;android-36`,
   `platforms;android-35`, `build-tools;35.0.0`; `ANDROID_HOME` definido y
   licencias aceptadas (`sdkmanager --licenses`).
3. **Modo de desarrollador** de Windows activado (Flet necesita symlinks).

Compilar:

```bash
pipenv run flet build apk
```

El resultado queda en `build/apk/cruz-de-la-suerte.apk`. Instalar con
`adb install -r build/apk/cruz-de-la-suerte.apk` o copiándolo al teléfono.

## Pendientes conocidos

- El APK pesa ~136 MB (runtime de Python + Flutter). Reducir con
  `flet build apk --split-per-abi`.
- Firmar siempre con la misma keystore (`--android-signing-key-store`) para poder
  actualizar sin desinstalar.
