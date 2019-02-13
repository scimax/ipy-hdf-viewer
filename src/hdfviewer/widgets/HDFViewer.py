import io
import os

import numpy as np

import h5py

import matplotlib.pyplot as plt

import ipywidgets as widgets

from hdfviewer.viewers.MplDataViewer import MplDataViewer, MplDataViewerError

from hdfviewer.widgets.MplOutput import MplOutput

class HDFViewerError(Exception):
    """:class:`HDFViewer` specific exception"""

    pass

class HDFViewer(widgets.Accordion):
    """This class allows to inspect HDF data in the context of **Jupyter Lab**

    It represents each group found in the HDF file as an accordion made of the following subitems:

    - **attributes**: contains the HDF attributes of this group
    - **groups**: contains the HDF subgroups of this group 
    - **datasets**: contains the HDF datasets of this group

    If one of these subitems is empty (e.g. no attributes defined for a given group) the corresponding subitem is omitted.
    When one reaches a HDF dataset, informations about the dataset are collected (dimensionality, numeric type, attributes ...) and displayed in a Jupyter output widget. In case of 1D, 2D or 3D dataset, a view of the dataset is also displayed. Depending on the dimensionality of the dataset the display will consist in:

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
       :caption: Usage in a Jupyter Lab notebook

       %matplotlib ipympl

       import h5py
       from hdfviewer.widgets.HDFViewer import HDFViewer
       from hdfviewer.widgets.PathSelector import PathSelector

       path = PathSelector(extensions=[".hdf",".h5",".nxs"])
       path.widget

       if path.file:
           hdf5 = h5py.File(path.file,"r")
           display(HDFViewer(hdf5))

    :param hdf: the hdf Data to be inspected.

        - for `str` input type, this will be the path to the HDF datafile
        - for `File`, this will be the output of a prior HDF file opening in read mode
        - for `bytes`, this will the byte representation of athe HDF data
    :type hdf: str or bytes or h5py:File
    :param startPath: the hdf path from where the HDF data will be inspected.

        If not set, the starting path will be the root of the HDF data
    :type startPath: str or None

    :raises: :class:`HDFViewerError`: if the HDF data could not be set properly
    """

    def __init__(self, hdf, startPath=None):
        
        widgets.Accordion.__init__(self)
            
        try:
            if isinstance(hdf,h5py.File) and hdf.mode=="r":
                self._hdf = hdf
            elif isinstance(hdf,str):
                self._hdf = h5py.File(hdf,"r")
            elif isinstance(hdf,bytes):
                self._hdf = h5py.File(io.BytesIO(hdf),"r")
            else:
                raise IOError("Invalid HDF stream")
        except Exception as e:
            raise HDFViewerError(str(e))

        if startPath is None:
            self._startPath = "/"
            self.children = [HDFViewer(hdf,self._startPath)]
            self.set_title(0,self._startPath)
        else:
            self._startPath = startPath
                        
            attributesAccordion = widgets.Accordion()
            for idx,(key,value) in enumerate(self._hdf[self._startPath].attrs.items()):
                attributesAccordion.children = list(attributesAccordion.children) + [widgets.HTML(value)]
                attributesAccordion.set_title(idx,key) 
                             
            # Setup the groups and datasets accordion
            groupsAccordion = widgets.Accordion()
            datasetsAccordion = widgets.Accordion()
            for value in list(self._hdf[self._startPath].values()):                
                if isinstance(value,h5py.Group):
                    groupsAccordion.children = list(groupsAccordion.children) + [HDFViewer(hdf,value.name)]
                    groupsAccordion.set_title(len(groupsAccordion.children)-1,value.name)
                elif isinstance(value,h5py.Dataset):
                    datasetInfo = []
                    shape = value.shape
                    # Set some informations about the current hdf value
                    datasetInfo.append("<i>Dimension: %s</i>" % str(shape))
                    datasetInfo.append("<i>Reduced dimension: %s</i>" % str(tuple([s for s in shape if s != 1])))
                    datasetInfo.append("<i>Type: %s</i>" % value.dtype.name)
                    datasetInfo = "<br>".join(datasetInfo)
                    vbox = widgets.VBox()
                    vbox.children = [widgets.HTML(datasetInfo),MplOutput()]
                    datasetsAccordion.children = list(datasetsAccordion.children) + [vbox]
                    datasetsAccordion.set_title(len(datasetsAccordion.children)-1,value.name) 
                    datasetsAccordion.observe(self._onSelectDataset,names="selected_index")

            # Display only the accordions which have children
            nestedAccordions = [("attributes",attributesAccordion),("groups",groupsAccordion),("datasets",datasetsAccordion)]
            for title,acc in nestedAccordions:
                if not acc.children:
                    continue
                acc.selected_index = None
                self.children = list(self.children) + [acc]
                self.set_title(len(self.children)-1,title)
                                        
        # By default, the accordion is closed at start-up
        self.selected_index = None
                                              
    def _onSelectDataset(self,change):
        """A callable that is called when a new dataset is selected

        See `here <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Events.html#Traitlet-events>`_ for more information
        """
                                
        idx = change["new"]
        
        # If the accordions is closed does nothing
        if idx is None:
            return
        
        accordion = change["owner"]
                        
        path = accordion.get_title(idx)
                        
        vbox = accordion.children[idx]
        
        output = vbox.children[1]
        output.clear_output(wait=False)
        
        with output:
            try:
                self._viewer = MplDataViewer(self._hdf[path],standAlone=False)
            except MplDataViewerError as e:
                label = widgets.Label(value=str(e))
                display(label)                
            else:
                # Bind the DataViewer figure to the MplOutput widget for allowing a "clean" output clearing (i.e. release the figure from plt)
                output.figure = self._viewer.viewer.figure

        hbox = widgets.HBox()

        firstFrame = widgets.Button(description="first frame")
        previousFrame = widgets.Button(description="previous frame")
        nextFrame = widgets.Button(description="next frame")
        lastFrame = widgets.Button(description="last frame")
        frame = widgets.IntSlider(value=5,min=0,max=10)
        plotMode = widgets.Checkbox(value=False,description="xy integration")

        hbox.children = [firstFrame,previousFrame,frame,nextFrame,lastFrame,plotMode]
        display(hbox)

