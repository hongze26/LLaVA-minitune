import os
import webbrowser
from threading import Timer
from app import create_app

apps = create_app()

def open_browser():
    webbrowser.open("http://127.0.0.1:8000/static/index.html#/page/emotional_analysis.html")

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        Timer(1, open_browser).start()
    apps.run(port=8000, debug=True)
