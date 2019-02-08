#!/usr/bin/env python

"""
MatPlotLib based viewer for 1D NumPy data.

"""

import numpy as np

import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt

class _MplDataViewer1D(object):
    
    def __init__(self,dataset,**kwargs):
                            
        self._figure = plt.figure()

        self._initLayout()

        self.dataset = dataset

        plt.show(self._figure)
                   
    @property
    def figure(self):
        return self._figure
        
    @property
    def dataset(self):
        return self._dataset

    @dataset.setter                
    def dataset(self,dataset):
        """1D dataset setter
        """

        self._dataset = dataset
                        
        self.update()
        
    def _initLayout(self):
        """Initializes layout.
        """

        self._mainAxes = plt.subplot(111)
                            
    def update(self):

        self._mainAxes.plot(self._dataset[:])

        plt.draw()

if __name__ == "__main__":

    data = np.random.uniform(0,1,(1000,))

    d = DataViewer1D(data)

    plt.show()

                
