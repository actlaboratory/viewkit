import os
import sys
from .app import App
from . import creator
from .context import ApplicationContext, WindowContext
from .feature import Feature, FeatureStore
from .mainwnd import MainWindow
from .subwnd import SubWindow
from .menu import TopMenuDefinition, MenuItemDefinition, MenuDefinition, separator
from .settings import CustomSettingField
from .dialog import *

def run(ctx, first_window):
    app = App(ctx, first_window)
    app.run()
