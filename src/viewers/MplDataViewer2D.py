"""
MatPlotLib based viewer for 2D NumPy data.

"""

import numpy as np

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

class _MplDataViewer2D(object):
    
    def __init__(self,dataset,standAlone=True):
        
        self._standAlone = standAlone
                    
        self._figure = plt.figure()

        self.dataset = dataset

        self._initLayout()

        self._initActions()

        self.update()

        self.setXYIntegrationMode(False)

        plt.show(self._figure)
                   
    @property
    def figure(self):
        return self._figure
        
    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self,dataset):
        """2D dataset setter
        """

        self._dataset = dataset
                
        self._colorbar = None

        self._selectedRows = slice(0,1,None)
        self._selectedCols = slice(0,1,None)

        self._rowSlice = slice(0,self._dataset.shape[0],None)
        self._colSlice = slice(0,self._dataset.shape[1],None)
        
    def _onChangeAxesLimits(self,event):
        """Update the cross plot according to the reduced row and/or column range
        """

        self._rowSlice = slice(*sorted([int(v) for v in event.get_ylim()]))
        self._colSlice = slice(*sorted([int(v) for v in event.get_xlim()]))
        
        data = self._dataset[self._rowSlice,self._colSlice]

        if self._colorbar:
            self._colorbar.set_clim(vmin=data.min(),vmax=data.max())
            self._colorbar.draw_all()

        self._updateCrossPlot()

    def _initActions(self):
        """Init all the widgets actions.
        """

        self._buttonPressId = self._figure.canvas.mpl_connect('button_press_event', self._onSelectPixel)
        self._keyPressId = self._figure.canvas.mpl_connect('key_press_event', self._onKeyPress)

        self._mainAxes.callbacks.connect('ylim_changed', self._onChangeAxesLimits)

    def _initLayout(self):
        """Initializes layout.
           The figure is made of an central image surrounded on top by the column-view of the dataset and on the right by a row-view of the dataset
           which depending on the plotting mode corresponds to:
               - slices along the row and column of a selected pixel using left-click mouse button when the cross-plot mode is set
               - integrations of the 2D image along the X and Y axis when the integration mode is set
        """

        grid = gridspec.GridSpec(3, 3, self._figure, width_ratios=[0.3, 4, 1], height_ratios=[1, 4, 0.3], wspace=0.3)

        self._mainAxes = plt.subplot(grid[1,1])
        self._mainAxes.set_xlim([0,self._dataset.shape[1]])
        self._mainAxes.set_ylim([0,self._dataset.shape[0]])
        if self._standAlone:
            self._cursor = widgets.Cursor(self._mainAxes,useblit=True)

        self._cbarAxes = plt.subplot(grid[1,0])
        self._rowSliceAxes = plt.subplot(grid[0,1])
        self._rowSliceAxes.xaxis.set_tick_params(bottom=False,labelbottom=False,top=True,labeltop=True)
        self._colSliceAxes = plt.subplot(grid[1,2])
        self._colSliceAxes.tick_params(axis="x",rotation=270)
        self._colSliceAxes.yaxis.set_tick_params(bottom=False,labelbottom=False,top=True,labeltop=True)

        self._image = None

        self._selectedPixel = (0,0)
        
    def _onKeyPress(self,event):
        """Add keyboard interaction for navigating through the dataset
        """

        if event.key == "i":
            self.setXYIntegrationMode(not self._xyIntegration)

        self._updateCrossPlot()

    def _onSelectPixel(self,event):
        """Update the cross plot according to the selected pixel of the 2D/3D image.
        """

        # Only left button click will produce a cross plot
        if event.button != 1:
            return

        if not event.inaxes or (event.inaxes.axes != self._mainAxes):
            return
        
        self.selectPixel(int(event.ydata),int(event.xdata))
        
    def _updateCrossPlot(self):
        """Update the cross plots for 2D/3D dataset.
           Cross plots are 1D plots which correspond to the reduced view of 2D/3D datasets projected onto X and Y axis            
        """
         
        if self._xyIntegration:
            self._selectedRows = self._rowSlice
            self._selectedCols = self._colSlice
        else:
            row,col = self._selectedPixel
            self._selectedRows = slice(row,row+1,None)
            self._selectedCols = slice(col,col+1,None)

        self._rowSliceAxes.clear()        
        xValues = np.arange(*self._colSlice.indices(self._colSlice.stop))
        yValues = np.sum(self._dataset[self._selectedRows,self._colSlice],axis=0)
        self._rowSliceAxes.plot(xValues,yValues)
        self._rowSliceAxes.set_xlim(min(xValues),max(xValues))
        self._rowSliceAxes.set_ylim(min(yValues),max(yValues))
                
        self._colSliceAxes.clear()                
        xValues = np.arange(*self._rowSlice.indices(self._rowSlice.stop))
        yValues = np.sum(self._dataset[self._rowSlice,self._selectedCols],axis=1)
        self._colSliceAxes.plot(yValues,xValues)
        self._colSliceAxes.set_xlim(min(yValues),max(yValues))
        self._colSliceAxes.set_ylim(min(xValues),max(xValues))

        plt.draw()

    def selectPixel(self,row,col):
        """Select a pixel on the image and update the cross plots
        """

        self._selectedPixel = (row,col)

        self._updateCrossPlot()
                            
    def setXYIntegrationMode(self,xyIntegration):
        """Toggle the integration mode.
           If True, the top and right 1D plots will be resp. the sum/integral over y and x axis
           If False, the top and right 1D plots will be resp. the cross plots along corresonding to resp. y and x axis of the selected pixel
        """

        self._xyIntegration = xyIntegration

        self._figure.canvas.toolbar.set_message("XY integration mode activated" if self._xyIntegration else "Cross-plot mode activated")
        if self._standAlone:
            self._cursor.set_active(not self._xyIntegration)

        self._updateCrossPlot()

    def update(self):

        # Remove the current image if any
        if self._image:
            self._image.remove()

        self._image = self._mainAxes.imshow(self._dataset[:,:],aspect="auto",origin="lower")

        if self._colorbar is None:
            self._colorbar = self._figure.colorbar(self._image, cax=self._cbarAxes)
            self._colorbar.ax.yaxis.set_ticks_position('left')

        plt.draw()

if __name__ == "__main__":

    data = np.random.uniform(0,1,(100,200))

    d = DataViewer2D(data)

    plt.show()

                
