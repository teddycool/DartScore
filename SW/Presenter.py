__author__ = 'teddycool'
# Propose of this module is to create and return a 'presenter'-device for the selected environment
# Presenter is used for viewing of the videostream, either as a background for the GUI or for debugging



def createPresenter(type):
    if type == "FRONTEND":
        from FrontEnd.FrontEnd  import FrontEnd
        presenter = FrontEnd(1024,768) #screen-size
        return presenter

