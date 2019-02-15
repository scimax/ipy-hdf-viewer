import io
import os
import webbrowser

import numpy as np

import h5py

import matplotlib.pyplot as plt

import ipywidgets as widgets

from hdfviewer import __version__
from hdfviewer.viewers.MplDataViewer import MplDataViewer, MplDataViewerError
from hdfviewer.widgets.MplOutput import MplOutput

def HDFViewerWidget(hdf, startPath=None):

    vbox = widgets.VBox()

    button = widgets.Button(description="documentation", tooltip="open documentation for release {0}".format(__version__))

    button.on_click(lambda event : HDFViewer.info())

    vbox.children = [button,HDFViewer(hdf,startPath)]

    return vbox

class HDFViewerError(Exception):
    """:class:`HDFViewer` specific exception"""

    pass

class HDFViewer(widgets.Accordion):
    """This class allows to inspect HDF data in the context of **Jupyter Lab**

    .. include:: ../README.rst
       :start-after: overview-begin
       :end-before: overview-end

    .. include:: ../README.rst
       :start-after: usage-begin
       :end-before: usage-end

    :param hdf: the hdf Data to be inspected.

        - for `str` input type, this will be the path to the HDF datafile
        - for `File`, this will be the output of a prior HDF file opening in read mode
        - for `bytes`, this will the byte representation of athe HDF data
    :type hdf: str or bytes or :class:`h5py.File`
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

        See `here <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Events.html#Traitlet-events>`__ for more information
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

    @staticmethod
    def info(version=None):
        """Open the url of a given release of the package documentation.

        :param release: the release of the package.
            
            If None, the current release will be selected.
        :type release: str
        """

        version = version if version else __version__

        # This will open the package documentation stored on readthedocs
        url = os.path.join("https://hdf-viewer.readthedocs.io/en/{0}".format(version))
        webbrowser.open(url)

