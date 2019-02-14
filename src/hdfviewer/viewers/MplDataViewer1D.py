"""
MatPlotLib viewer for NumPy 1D NumPy data.
"""

import numpy as np

import matplotlib.pyplot as plt

class _MplDataViewer1D(object):
    """This class allows to display 1D NumPy array in a :class:`matplotlib.figure.Figure`

    This will be a simple matplotlib plot.

    :param dataset: the NumPy array to be displayed
        
        The dataset will be squeezed from any dimensions equal to 1
    :type dataset: :class:`numpy.ndarray`

    :param `kwargs`: the keyword arguments
    :type `kwargs`: dict
    """
    
    def __init__(self,dataset,**kwargs):
                            
        self._figure = plt.figure()

        self._initLayout()

        self.dataset = dataset

        plt.show(self._figure)
                   
    @property
    def figure(self):
        """Getter for the figure to be displayed.

        :return: returns the figure to be displayed in the jupyter output widget
        :rtype: :class:`matplotlib.figure.Figure`
        """

        return self._figure
        
    @property
    def dataset(self):
        """Getter/setter for the dataset to be displayed.

        :getter: returns the dataset to be displayed
        :setter: sets the dataset to be displayed
        :type: :class:`numpy.ndarray`
        """

        return self._dataset

    @dataset.setter                
    def dataset(self,dataset):

        self._dataset = dataset
                        
        self.update()
        
    def _initLayout(self):
        """Initializes the figure layout.
        """

        self._mainAxes = plt.subplot(111)
                            
    def update(self):
        """Update the figure.
        """

        self._mainAxes.plot(self._dataset[:])

        plt.draw()

if __name__ == "__main__":

    data = np.random.uniform(0,1,(1000,))

    d = DataViewer1D(data)

    plt.show()

                
