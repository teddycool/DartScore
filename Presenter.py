__author__ = 'teddycool'
# Propose of this module is to create and return a 'presenter'-device for the selected environment
# Presenter is used for viewing of the videostream, either as a background for the GUI or for debugging



def createPresenter(type):
    if type == "PC":
        from WinSetup.VideoPresenter import VideoPresenter
        presenter = VideoPresenter()
        return presenter
    elif type == "PI":
        from PiSetup.PiPresenter import  VideoPresenter
        presenter = VideoPresenter()
        return presenter
    elif type == "VIDEO":
        from WinSetup.VideoPresenter  import VideoPresenter
        presenter = VideoPresenter()
        return presenter

