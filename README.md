# Mesa de Soporte TI — Doble aplicación de escritorio

Proyecto preparado para abrir directamente en **Visual Studio Code**.

## Cómo funciona

Hay dos aplicaciones distintas que trabajan sobre la misma base de datos SQLite:

### 1. Aplicación Usuario
Archivo:
`frontend_usuario/app_usuario.py`

Permite:
- seleccionar al solicitante,
- crear un ticket,
- escribir título y descripción,
- seleccionar categoría,
- seleccionar prioridad,
- enviar el ticket,
- consultar los tickets de ese solicitante,
- ver estado y responsable.

### 2. Aplicación Equipo TI
Archivo:
`frontend_ti/app_ti.py`

Permite:
- recibir todos los tickets,
- ver el solicitante,
- ver prioridad y estado,
- asignar responsable,
- cambiar el estado,
- consultar historial de cambios,
- ver un resumen por estado.

La aplicación TI actualiza el listado automáticamente cada 5 segundos.

## Base de datos compartida

Ambas aplicaciones utilizan:

`database/mesa_soporte.db`

Por eso, si el usuario crea un ticket en la aplicación de usuario, aparecerá en la aplicación del equipo TI.

SQLite está configurado con WAL para permitir que ambas aplicaciones estén abiertas al mismo tiempo.

## Abrir en Visual Studio Code

1. Descomprime el ZIP.
2. Abre Visual Studio Code.
3. Ve a **Archivo > Abrir carpeta**.
4. Selecciona la carpeta `MesaSoporteTI_DobleApp_VSCode`.
5. Instala la extensión oficial de Python si VS Code te la solicita.
6. Presiona `Ctrl + Shift + D`.
7. En la parte superior puedes elegir:
   - `Abrir App Usuario`
   - `Abrir App Equipo TI`
   - `Abrir las dos aplicaciones`

También puedes abrir el archivo:

`MesaSoporteTI.code-workspace`

## Ejecutar desde terminal de VS Code

Usuario:
```bash
python frontend_usuario/app_usuario.py
```

Equipo TI:
```bash
python frontend_ti/app_ti.py
```

## Ejecutar sin VS Code

Puedes hacer doble clic en:

- `ABRIR_USUARIO.bat`
- `ABRIR_EQUIPO_TI.bat`
- `ABRIR_AMBAS.bat`

## Estructura

```text
MesaSoporteTI_DobleApp_VSCode/
├── backend/
│   ├── __init__.py
│   └── database.py
├── frontend_usuario/
│   └── app_usuario.py
├── frontend_ti/
│   └── app_ti.py
├── database/
│   ├── mesa_soporte.db
│   ├── schema.sql
│   └── seed.sql
├── tests/
│   └── test_integracion.py
├── .vscode/
│   ├── launch.json
│   └── tasks.json
├── MesaSoporteTI.code-workspace
├── ABRIR_USUARIO.bat
├── ABRIR_EQUIPO_TI.bat
└── ABRIR_AMBAS.bat
```

## Hito 3

La separación en dos interfaces sigue manteniendo el alcance del Hito 3:
- RF-01 registrar solicitud,
- RF-02 ID y fecha automáticos,
- RF-03 listado,
- RF-04 asignación de responsable y cambio de estado.

No incluye autenticación. El solicitante se selecciona de una lista, tal como quedó definido en el alcance del proyecto.
