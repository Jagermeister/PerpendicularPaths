from view import viewfactory as vf
from model import core as pp

def main():
	model = pp.core()
	view = vf.createFactory()
	view.init(model)
	while view.handle_events():
		view.update()
		view.display()
	view.quit()

if __name__ == '__main__': main()