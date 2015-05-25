"""Entry point for game"""
from view import viewfactory as vf
from model import core as pp

def main():
    """simple game loop to link a view with our model logic"""
    model = pp.PerpendicularPaths()
    view = vf.factory_create()
    view.init(model)
    while 1:
        view.handle_events()
        view.update()
        view.display()
    view.quit()

if __name__ == '__main__':
    main()
