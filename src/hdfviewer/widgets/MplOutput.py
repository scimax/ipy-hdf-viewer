import matplotlib.pyplot as plt

from ipywidgets import widgets

class MplOutput(widgets.Output):
    
    def __init__(self,figure=None,**kwargs):
        
        widgets.Output.__init__(self,**kwargs)
        
        self._figure = figure
        
    @property
    def figure(self):
        
        return self._figure
    
    @figure.setter
    def figure(self,figure):
        
        self._figure = figure
        
    def clear_output(self,**kwargs):
                
        widgets.Output.clear_output(self,**kwargs)
        
        if self._figure:
            plt.close(self._figure)
            del self._figure
