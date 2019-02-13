"""
MatPlotLib based viewer for 1D, 2D and 3D NumPy data.
"""

import numpy as np

import warnings
warnings.filterwarnings("ignore")

from hdfviewer.viewers.MplDataViewer1D import _MplDataViewer1D
from hdfviewer.viewers.MplDataViewer2D import _MplDataViewer2D
from hdfviewer.viewers.MplDataViewer3D import _MplDataViewer3D

_viewers = {1 : _MplDataViewer1D, 2 : _MplDataViewer2D, 3 : _MplDataViewer3D}

class MplDataViewerError(Exception):
    pass

class MplDataViewer(object):
    
    def __init__(self,dataset,standAlone=True):

        # Remove axis with that has dimension 1 (e.g. (20,1,30) --> (20,30))
        self._dataset = np.squeeze(dataset)

        ndim = self._dataset.ndim
        if ndim not in _viewers:
            raise MplDataViewerError("The dataset dimension ({ndim:d}) is not supported by the viewer".format(ndim=ndim))

        self._viewer = _viewers[ndim](self._dataset,standAlone)
                            
    @property
    def viewer(self):
        return self._viewer
                   
if __name__ == "__main__":

    import numpy as np
    import matplotlib.pyplot as plt

    dataset = np.random.uniform(0,1,(100,400,30))

    d = MplDataViewer(dataset)

                
