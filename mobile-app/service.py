#!/usr/bin/env python3
"""
Serviço em segundo plano do Magnus Wealth
Mantém servidor Flask rodando mesmo com app fechado
"""

from jnius import autoclass
from android.runnable import run_on_ui_thread
import time

PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)

# Importar e rodar servidor
from main import run_flask

if __name__ == '__main__':
    print("🚀 Serviço Magnus iniciado")
    run_flask()

