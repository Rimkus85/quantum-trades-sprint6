[app]
title = Magnus Wealth
package.name = magnuswealth
package.domain = com.magnus

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,flask,python-binance,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,FOREGROUND_SERVICE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.archs = arm64-v8a,armeabi-v7a

services = MagnusService:service.py:foreground

[buildozer]
log_level = 2
warn_on_root = 1

