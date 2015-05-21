from .native import nativeview
from .terminal import terminalview
from model.primative import shared as s

def createFactory():
	config = s.Shared.config()
	if config['view']['concrete'] == "native":
		return nativeview.nativeview()
	elif config['view']['concrete'] == "terminal":
		return terminalview.terminalview()
	elif config['view']['concrete'] == "terminal":
		pass
	else:
		raise Exception ("Concrete view '" + config['view']['concrete'] + "' was not found")