import os

import numpy as np

import h5py

import matplotlib.pyplot as plt

import ipywidgets as widgets

from hdfviewer.viewers.MplDataViewer import MplDataViewer, MplDataViewerError

from hdfviewer.widgets.MplOutput import MplOutput

class HDFViewer(widgets.Accordion):

    def __init__(self, hdf, startPath=None):
        
        widgets.Accordion.__init__(self)
            
        self._hdf = hdf
                
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

