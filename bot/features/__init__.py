# bot/features/__init__.py
import importlib
import pkgutil
from telegram.ext import Application

def load_features(application: Application):
    """Автоматически импортирует все модули в features и вызывает setup()"""
    package = __name__
    for _, name, _ in pkgutil.iter_modules(__path__, package + "."):
        module = importlib.import_module(name)
        if hasattr(module, "setup"):
            module.setup(application)
    print(f"✅ Загружено {len(list(pkgutil.iter_modules(__path__)))} модулей-функций")
