"""Template for views - these features should be fulfilled to interact with main.py"""
class ViewInterface:
    """Basic game loop functions"""
    def init(self, model):
        """Initialization, local use of model information"""
        pass

    def handle_events(self):
        """Process actions and interact with model"""
        pass

    def update(self):
        """Internal state of view objects"""
        pass

    def display(self):
        """Visual display of state"""
        pass

    def quit(self):
        """Unload any assets before exit"""
        pass
