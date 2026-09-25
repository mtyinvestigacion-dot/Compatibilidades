from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Sistema de Compatibilidades - MI Global")
    print("=" * 50)
    print("\n  Abre tu navegador en: http://localhost:5003\n")
    app.run(debug=True, host='0.0.0.0', port=5003)
