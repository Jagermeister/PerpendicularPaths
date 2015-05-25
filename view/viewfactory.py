"""Based on configuration, select which view will be used in main.py"""
from .native import nativeview
from .terminal import terminalview
from model.primative import shared as s

def factory_create():
    """return like view.viewinterface"""
    config = s.Shared.config()
    if config['view']['concrete'] == "native":
        return nativeview.NativeView()
    elif config['view']['concrete'] == "terminal":
        return terminalview.TerminalView()
    elif config['view']['concrete'] == "graphical":
        pass
    else:
        raise Exception("Concrete view '" + config['view']['concrete'] + "' was not found")
