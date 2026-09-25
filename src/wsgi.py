"""
Entrypoint para PythonAnywhere.

En el archivo WSGI que genera PythonAnywhere (pestaña Web -> WSGI configuration file),
reemplaza su contenido por:

    import sys, os
    sys.path.insert(0, '/home/<tu_usuario>/sistema-compatibilidades/src')
    os.environ['SECRET_KEY'] = '<valor real, generado una sola vez>'
    from wsgi import application

Ver DEPLOY.md para la guia completa paso a paso.
"""
from app import create_app

application = create_app()
