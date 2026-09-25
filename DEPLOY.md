# Desplegar en PythonAnywhere (plan gratuito)

Guia paso a paso para que el Sistema de Compatibilidades sea accesible desde
cualquier dispositivo, no solo desde esta PC. Se eligio PythonAnywhere free tier
en vez de Render porque su disco es persistente — SQLite no pierde datos en cada
reinicio/redeploy, a diferencia del disco efimero de Render free tier.

**Importante:** el plan gratuito no tiene UI de "variables de entorno" — el
`SECRET_KEY` se pega directo en el archivo WSGI (paso 6). Tambien: la app web
gratuita se desactiva si nadie entra al dashboard en ~1 mes — hay que loguearse
ahi de vez en cuando o el sitio se cae (los datos no se pierden, solo la app deja
de responder hasta que la reactives).

## 1. Crear la cuenta

Ve a https://www.pythonanywhere.com y crea una cuenta **Beginner** (gratis) con el
usuario/correo que prefieras. Ese `<usuario>` de PythonAnywhere será parte de tu URL:
`https://<usuario>.pythonanywhere.com`.

## 2. Subir el codigo

Como todavia no hay un repo remoto (solo git local), la forma mas simple es subir un
zip:

1. En tu PC: comprime la carpeta `sistema-compatibilidades` (sin `__pycache__`, sin
   `*.db`) en un `.zip`.
2. En PythonAnywhere, pestaña **Files** → sube el `.zip` a tu home (`/home/<usuario>/`).
3. Abre una consola **Bash** (pestaña Consoles → Bash) y descomprime:
   ```bash
   unzip sistema-compatibilidades.zip
   ```

Cuando exista un remoto en GitHub, los redeploys futuros seran simplemente
`git pull` en esa misma consola Bash, seguido del paso 8 (Reload).

## 3. Crear el virtualenv e instalar dependencias

En la misma consola Bash:

```bash
mkvirtualenv --python=python3.10 compatibilidades-venv
cd sistema-compatibilidades
pip install -r requirements.txt
```

## 4. Crear el primer usuario admin

Todavia dentro del virtualenv activado:

```bash
python scripts/seed_admin.py
```

Sigue las instrucciones en pantalla (usuario + contraseña). Guarda esa contraseña
en un lugar seguro — es la unica cuenta que puede crear a las demas.

## 5. Configurar la Web App — Manual configuration

Pestaña **Web** → **Add a new web app** → elige **Manual configuration** (NO uses
el wizard de Flask) → selecciona la version de Python que coincida con el
virtualenv (3.10).

En la seccion **Code** de esa misma pagina, configura:

- **Source code**: `/home/<usuario>/sistema-compatibilidades`
- **Working directory**: `/home/<usuario>/sistema-compatibilidades/src`
- **Virtualenv**: `/home/<usuario>/.virtualenvs/compatibilidades-venv`

No hay que mapear ninguna carpeta de **Static files** — todo el CSS/JS (Bootstrap,
iconos) se carga desde CDN, no hay assets locales que servir.

## 6. Editar el archivo WSGI

En la pestaña Web, seccion **Code**, hay un link al **WSGI configuration file**
(algo como `/var/www/<usuario>_pythonanywhere_com_wsgi.py`). Abrelo y reemplaza
TODO su contenido por:

```python
import sys
import os

sys.path.insert(0, '/home/<usuario>/sistema-compatibilidades/src')
os.environ['SECRET_KEY'] = '<pega aqui un valor aleatorio largo, generado una sola vez>'

from wsgi import application
```

Para generar un `SECRET_KEY` random puedes correr en la consola Bash:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 7. Reload

Pestaña Web → boton verde **Reload**.

## 8. Probar

Abre `https://<usuario>.pythonanywhere.com`, inicia sesion con el admin creado en
el paso 4.

## Mantenimiento recurrente (plan gratuito)

- **Login periodico**: entra al dashboard de PythonAnywhere al menos cada mes para
  que la app no se desactive por inactividad.
- **Backups manuales**: no hay backups automaticos en el plan gratuito. De vez en
  cuando, baja una copia de `src/compatibilidades.db` desde la pestaña Files.
- **Redeploys futuros**: si subes cambios de codigo (via `git pull` o volviendo a
  subir el zip), siempre hay que darle **Reload** en la pestaña Web para que se
  reflejen — no hay auto-deploy.
