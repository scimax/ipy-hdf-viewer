import matplotlib.pyplot as plt

from ipywidgets import widgets

class MplOutput(widgets.Output):
    """This class allows to open a matplotlib figre in a **Jupyter Lab**

    It derived from `ipywidgets.widgets.Output <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html#Output>`_ to circumvent from the 
    fact that when the cell is cleared and reloaded the figure is not removed from the matplotlib side. This ends up with a neverending increasing number 
    of registered figures. See `here <https://github.com/matplotlib/jupyter-matplotlib/issues/4>`__ for complementary informations.

    :param figure: the figure to be displayed in the output widget
    :type figure: :class:`matplotlib.figure.Figure`

    :param `**kwargs`: the keyword arguments to be passed to the parent class
    :type `**kwargs`: dict
    """
    def __init__(self,figure=None,**kwargs):
        
        widgets.Output.__init__(self,**kwargs)
        
        self._figure = figure
        
    @property
    def figure(self):
        """Getter/setter for the figure to be displayed in the jupyter output widget

        :getter: returns the figure to be displayed in the jupyter output widget
        :setter: sets the figure to be displayed in the jupyter output widget
        :type: :class:`matplotlib.figure.Figure`
        """
        
        return self._figure
    
    @figure.setter
    def figure(self,figure):
        
        self._figure = figure
        
    def clear_output(self,**kwargs):
        """Clear the jupyter output widget

        :param `**kwargs`: the keyword arguments to be forwarded to the corresponding parent class method
        :type `**kwargs`: dict
        """
                
        widgets.Output.clear_output(self,**kwargs)
        
        if self._figure:
            plt.close(self._figure)
            del self._figure
