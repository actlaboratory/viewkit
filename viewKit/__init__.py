import os
import sys
from .app import App
from . import creator
from .context import ApplicationContext, WindowContext
from .mainwnd import MainWindow


def run(ctx, first_window):
    # dllを相対パスで指定した時のため、カレントディレクトリを変更
    if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
        os.add_dll_directory(os.getcwd())
        sys.path.append(os.getcwd())
    app = App(ctx, first_window)
    app.run()
