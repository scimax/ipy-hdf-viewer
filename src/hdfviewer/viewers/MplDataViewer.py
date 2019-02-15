"""
MatPlotLib viewer for NumPy 1D, 2D and 3D NumPy data.
"""

import numpy as np

import warnings
warnings.filterwarnings("ignore")

from hdfviewer.viewers.MplDataViewer1D import _MplDataViewer1D
from hdfviewer.viewers.MplDataViewer2D import _MplDataViewer2D
from hdfviewer.viewers.MplDataViewer3D import _MplDataViewer3D

_viewers = {1 : _MplDataViewer1D, 2 : _MplDataViewer2D, 3 : _MplDataViewer3D}

class MplDataViewerError(Exception):
    """:class:`MplDataViewer` specific exception"""

    pass

class MplDataViewer(object):
    """This class allows to display 1D,2D or 3D NumPy array in a :class:`matplotlib.figure.Figure`

    Depending on the dimensionality of the dataset the display will consist in:

    - **1D**: simple MatPlotLib 1D plot
    - **2D**: matrix view of the dataset
    - **3D**: matrix view of the dataset

    In case of **2D** and **3D** datasets, the matrix view is made of a 2D image of the selected frame of the dataset (always `0` for 2D datasets) with a 1D column-projection view of the dataset on its top and a 1D row-projection view of the dataset on its right. The matrix view is interactive with the following interactions:

    - **2D**:

      - toggle between cross and integration 1D potting mode. In cross plot mode, the 1D projection views represents resp. the row and column of the matrix image point left-clicked by the user. In integration plot mode, the 1D projection views represents the sum over resp. the row and column of the image. To switch between those two modes, press the **i** key.
    - **3D**:

      - toggle between cross and integration 1D potting mode. See above.
      - go to the last frame by pressing the **pgdn** key.
      - go to the first frame by pressing the **pgup** key.
      - go to the next frame by pressing the **down** or the **right** keys or wheeling **down** the mouse wheel
      - go to the previous frame by pressing the **up** or the **left** keys or wheeling **up** the mouse down
      - go the +n (n can be > 9) frame by pressing *n* number followed by the **down** or the **right** keys 
      - go the -n (n can be > 9) frame by pressing *n* number followed by the **up** or the **left** keys 

    .. code-block:: python
       :caption: Example

        import numpy as np
        import matplotlib.pyplot as plt

        dataset = np.random.uniform(0,1,(100,400,30))

        d = MplDataViewer(dataset)

    :param dataset: the NumPy array to be displayed
        
        The dataset will be squeezed from any dimensions equal to 1
    :type dataset: :class:`numpy.ndarray`

    :param standAlone: if True a cursor will be displayed when hovering over the 2D view of the dataset (only for 2D or 3D datasets)
    :type standAlone: bool

    :raises: :class:`MplDataViewerError`: if the (squeezed) dataset has a dimension different from 1, 2 or 3 
    """

    def __init__(self,dataset,standAlone=True):

        # The viewer only supports array with numeric types
        if not np.issubdtype(dataset.dtype,np.number):
            raise MplDataViewerError("The dataset type ({dtype}) is not numeric".format(dtype=dataset.dtype))
            
        # Remove axis with that has dimension 1 (e.g. (20,1,30) --> (20,30))
        self._dataset = np.squeeze(dataset)

        ndim = self._dataset.ndim
        if ndim not in _viewers:
            raise MplDataViewerError("The dataset dimension ({ndim:d}) is not supported by the viewer".format(ndim=ndim))

        self._viewer = _viewers[ndim](self._dataset,standAlone=standAlone)
                            
    @property
    def viewer(self):
        """Getter for the dimension specific viewer.

        :return: the dimension specific viewer
        :rtype: :class:`_MplDataViewer1D` or :class:`_MplDataViewer2D` or :class:`_MplDataViewer3D`
        """
        return self._viewer
                   
if __name__ == "__main__":

    import numpy as np
    import matplotlib.pyplot as plt

    dataset = np.random.uniform(0,1,(100,400))

    d = MplDataViewer(dataset)

                
