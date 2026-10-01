# Sistema de Compatibilidades

Modulo para guardar y consultar que panel de reemplazo es compatible con que TV
completa (Marca + Modelo + Panel original que traia esa TV). Pensado para usarse
desde varios dispositivos a la vez, con cuentas de usuario reales.

## Modulos del Sistema

### 1. Login (`/login`, `/logout`)
Acceso mediante usuario/contraseña. No hay auto-registro: solo un admin puede dar
de alta cuentas nuevas (ver Usuarios). Toda la app exige sesion iniciada, incluso
para solo consultar.

### 2. Compatibilidades (`/compatibilidades/exitosas`, `/compatibilidades/fallidas`)
Cada compatibilidad tiene un campo `resultado` (`exitosa`/`fallida`, constante
`RESULTADOS` en `models.py`) que indica si la prueba de ese panel de reemplazo en
esa TV funciono o no. Son dos listados separados (dos entradas en el sidebar,
dos rutas), cada uno con su propia busqueda (por panel, marca, modelo o panel
original) y filtro por marca — ambos reutilizan `_listar_compatibilidades(resultado)`
y la misma plantilla `listar.html`. `/` redirige a `/compatibilidades/exitosas`.
Alta/edicion/baja (`activo=False`, nunca se borra) solo para admins; los viewers
solo consultan. El formulario de alta/edicion incluye el selector de Resultado
(el boton "Nueva" de cada listado precarga `?resultado=` segun en cual de las dos
pantallas estés). El alta/edicion de marca y modelo tiene autocomplete (datalist)
contra `/api/marcas` y `/api/modelos` (sin filtrar por resultado).

### 3. Importar Excel (`/compatibilidades/importar`) — solo admin
Carga masiva de compatibilidades desde un .xlsx (primera fila = encabezado,
columnas en el orden de `COLUMNAS_IMPORTACION` en `routes.py`, incluye `resultado`
como ultima columna opcional — vacio o "Exitosa"/"Fallida", default exitosa). Hay
una plantilla descargable (`/compatibilidades/importar/plantilla`). Por fila:
valida campos obligatorios (panel, marca, modelo, panel original), salta
duplicados exactos (misma combinación panel+marca+modelo+panel original ya activa,
sin importar el resultado) y reporta creadas/duplicadas/errores sin tumbar el
resto del archivo si una fila falla.

### 4. Usuarios (`/usuarios/...`) — solo admin
Alta de cuentas (usuario + contraseña + rol), activar/desactivar (nunca se borra
un usuario) y restablecer contraseña. El primer admin se crea con
`scripts/seed_admin.py`, no hay usuario/contraseña por defecto en el codigo.

## Roles

- **admin**: todo lo anterior, incluida gestion de usuarios.
- **viewer**: solo puede ver/buscar compatibilidades.

## Estructura del Proyecto

```
sistema-compatibilidades/
├── src/
│   ├── app/
│   │   ├── __init__.py     # Factory Flask, login manager, errorhandler 403
│   │   ├── auth.py         # login_manager, user_loader, admin_required
│   │   ├── models.py       # Usuario, Compatibilidad
│   │   └── routes.py       # Rutas y controladores (blueprint `main`)
│   ├── templates/
│   ├── static/
│   ├── config.py
│   ├── run.py
│   └── wsgi.py             # entrypoint para PythonAnywhere
├── scripts/
│   ├── run_dev.bat
│   └── seed_admin.py       # crea el primer usuario admin
├── requirements.txt
└── DEPLOY.md                # guia paso a paso para PythonAnywhere
```

## Ejecutar (local)

```bash
cd src
python run.py
# Abrir http://localhost:5003
```

Antes de la primera vez, crea el admin:

```bash
python scripts/seed_admin.py
```

## Tecnologias

- Flask 3.0 + Flask-SQLAlchemy + Flask-Login
- SQLite (con `connect_args={'timeout': 15}` para tolerar 2 dispositivos escribiendo casi al mismo tiempo)
- Bootstrap 5 + Bootstrap Icons (via CDN)
- Hash de contraseñas con `werkzeug.security` (incluido con Flask, sin libreria extra)

## Convenciones

- Mismas convenciones que `planeacion-paneles`/`kit-logistica-system`: Bootstrap 5,
  flash messages, soft delete (`activo=False`), sidebar con `menu-header`.
- **Diferencia clave con las otras apps**: esta si tiene autenticacion real (usuario/
  contraseña + roles) en vez del campo de texto libre "usuario". La trazabilidad de
  quien creo/edito una compatibilidad usa `creado_por_id`/`modificado_por_id` (FK a
  `Usuario`) en vez de un string libre.
- Guard de login: no hay `@login_required` en cada ruta, sino un `@main.before_request`
  global que exige sesion salvo en `/login`. Mas dificil de olvidar en una ruta nueva.
- Sin CSRF tokens (igual que las otras apps de Marco) — aceptable para herramienta
  interna detras de login, pero es la primera vez que hay cuentas reales, vale la
  pena tenerlo presente si el sistema crece.
- Sin `db.relationship()` — los FKs (`creado_por_id`, etc.) se resuelven con consultas
  manuales cuando se necesita mostrar el username.
- No hay Flask-Migrate/Alembic: los cambios de esquema sobre una DB ya existente se
  resuelven a mano con `ALTER TABLE` dentro de `create_app()` (ver
  `_migrar_columna_resultado` en `app/__init__.py`), chequeando con
  `db.inspect(db.engine)` si la columna ya existe antes de agregarla. Si se agrega
  otra columna a futuro sobre una tabla que ya tiene filas, seguir el mismo patron.

## Despliegue

Ver `DEPLOY.md` para subirlo a PythonAnywhere (plan gratuito, elegido porque su disco
es persistente y SQLite no se pierde entre reinicios, a diferencia de Render free tier).
