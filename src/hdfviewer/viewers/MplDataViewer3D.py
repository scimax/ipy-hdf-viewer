"""MatPlotLib based viewer for 2D NumPy data.
"""

import numpy as np

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

class _MplDataViewer3D(object):
    """This class allows to display 3D NumPy array in a :class:`matplotlib.figure.Figure`

    The figure is made of an central image surrounded on top by the column-view of the dataset and on the right by a row-view of the dataset
    which depending on the plotting mode corresponds to:

    - slices along the row and column of a selected pixel using left-click mouse button when the cross-plot mode is set
    - integrations of the 2D image along the X and Y axis when the integration mode is set

    The figure is interactive with the following interactions:

    - toggle between cross and integration 1D potting mode. In cross plot mode, the 1D projection views represents resp. the row and column of the matrix image point left-clicked by the user. In integration plot mode, the 1D projection views represents the sum over resp. the row and column of the image. To switch between those two modes, press the **i** key.
    - toggle between cross and integration 1D potting mode. See above.
    - go to the last frame by pressing the **pgdn** key.
    - go to the first frame by pressing the **pgup** key.
    - go to the next frame by pressing the **down** or the **right** keys or wheeling **down** the mouse wheel
    - go to the previous frame by pressing the **up** or the **left** keys or wheeling **up** the mouse down
    - go the +n (n can be > 9) frame by pressing *n* number followed by the **down** or the **right** keys 
    - go the -n (n can be > 9) frame by pressing *n* number followed by the **up** or the **left** keys 

    :param dataset: the NumPy array to be displayed
        
        The dataset will be squeezed from any dimensions equal to 1
    :type dataset: :class:`numpy.ndarray`

    :param standAlone: if True a cursor will be displayed when hovering over the 2D view of the dataset
    :type standAlone: bool
    """
    
    def __init__(self,dataset,standAlone=True):
        
        self._standAlone = standAlone

        self.dataset = dataset
                    
        self._figure = plt.figure()

        # Setup the figure layout depending on the data dimensionality
        self._initLayout()

        # Setup the widget events                            
        self._initActions()

        self.setSelectedFrame(0)

        self.setXYIntegrationMode(False)

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
        """3D dataset setter
        """

        self._dataset = dataset
        
        self._colorbar = None

        self._selectedRows = slice(0,1,None)
        self._selectedCols = slice(0,1,None)
        self._selectedFrame = 0

        self._rowSlice = slice(0,self._dataset.shape[0],None)
        self._colSlice = slice(0,self._dataset.shape[1],None)

    def _onChangeAxesLimits(self,event):
        """Callback called when the axis of the matrix view have changed.

        This will update the cross plot according to the reduced row and/or column range.

        :param event: the axes whose axis have been changed
        :type event: :class:`matplotlib.axes.SubplotBase`
        """

        self._rowSlice = slice(*sorted([int(v) for v in event.get_ylim()]))
        self._colSlice = slice(*sorted([int(v) for v in event.get_xlim()]))
        
        data = self._dataset[self._rowSlice,self._colSlice]

        if self._colorbar:
            self._colorbar.set_clim(vmin=data.min(),vmax=data.max())
            self._colorbar.draw_all()

        self._updateCrossPlot()

    def _initActions(self):
        """Setup all the actions and their corresponding callbacks.
        """

        # For 2D and 3D dataset clicking somewhere on the imshow plot will produce 2 plots corresponding to row and column slices
        self._scrollId = self._figure.canvas.mpl_connect('scroll_event', self._onScrollFrame)
        self._buttonPressId = self._figure.canvas.mpl_connect('button_press_event', self._onSelectPixel)
        self._keyPressId = self._figure.canvas.mpl_connect('key_press_event', self._onKeyPress)

        self._mainAxes.callbacks.connect('ylim_changed', self._onChangeAxesLimits)

    def _initLayout(self):
        """Initializes the figure layout.
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

        self._numericKeysBuffer = ""

        self._frameStep = 1

        self._selectedPixel = (0,0)
        
    def _onKeyPress(self,event):
        """Callback called when a keyboard key is pressed.

        :param event: the keyboard keypress event
        :type event: :class:`matplotlib.backend_bases.KeyEvent`
        """

        keyToSign = {"+" : 1, "right" : 1, "up" : 1, "-" : -1, "left" : -1, "down" : -1}
        if event.key in keyToSign:
            self.setSelectedFrame(self._selectedFrame+keyToSign[event.key]*self._frameStep)
            self._numericKeysBuffer = ""
        elif event.key == "pageup":
            self.setSelectedFrame(0)
        elif event.key == "pagedown":
            self.setSelectedFrame(self._dataset.shape[2]-1)
        elif event.key.isnumeric():
            self._numericKeysBuffer = self._numericKeysBuffer + event.key
            self._frameStep = int(self._numericKeysBuffer)
        elif event.key == "i":
            self.setXYIntegrationMode(not self._xyIntegration)

        self._updateCrossPlot()

    def _onScrollFrame(self,event):
        """Callback called when the mouse wheel is rolled.

         This will scroll to previous/next frame according to the mouse wheel direction.

        :param event: the mouse wheel event event
        :type event: :class:`matplotlib.backend_bases.MouseEvent`
        """

        incr = event.step if event.button == "up" else -event.step
        self.setSelectedFrame(self._selectedFrame+incr)
        self._updateCrossPlot()

    def _onSelectPixel(self,event):
        """Callback called when a mouse buttton is clicked.

        :param event: the mouse click event
        :type event: :class:`matplotlib.backend_bases.MouseEvent`
        """

        # Only left button click will produce a cross plot
        if event.button != 1:
            return

        if not event.inaxes or (event.inaxes.axes != self._mainAxes):
            return
        
        self.selectPixel(int(event.ydata),int(event.xdata))
        
    def _updateCrossPlot(self):
        """Update the cross plots.
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
        yValues = np.sum(self._dataset[self._selectedRows,self._colSlice,self._selectedFrame],axis=0)
        self._rowSliceAxes.plot(xValues,yValues)
        self._rowSliceAxes.set_xlim(min(xValues),max(xValues))
        self._rowSliceAxes.set_ylim(min(yValues),max(yValues))
                
        self._colSliceAxes.clear()                
        xValues = np.arange(*self._rowSlice.indices(self._rowSlice.stop))
        yValues = np.sum(self._dataset[self._rowSlice,self._selectedCols,self._selectedFrame],axis=1)
        self._colSliceAxes.plot(yValues,xValues)
        self._colSliceAxes.set_xlim(min(yValues),max(yValues))
        self._colSliceAxes.set_ylim(min(xValues),max(xValues))

        plt.draw()

    def selectPixel(self,row,col):
        """Select a pixel on the image.

        This will update the croos plots.

        :param row: the pixel row
        :type column: int
        :param row: the pixel column
        :type column: int
        """

        self._selectedPixel = (row,col)

        self._updateCrossPlot()
                            
    def setSelectedFrame(self,selectedFrame):
        """Set the frame to be displayed.

        :param selectedFrame: the new frame to be displayed
        :type selectedFrame: int
        """
        
        self._selectedFrame = min(max(selectedFrame,0),self._dataset.shape[2]-1)

        self._figure.canvas.toolbar.set_message("selected frame: %d" % self._selectedFrame)

        self.update()

    def setXYIntegrationMode(self,xyIntegration):
        """Switch between slice plot mode and integration mode.

        :param xyIntegration: if True, the croos plots will be resp. the integral over y and x axis otherwise the cross plots will be resp. slices along the selected pixel
        :type xyIntegration: bool
        """

        self._xyIntegration = xyIntegration

        self._figure.canvas.toolbar.set_message("XY integration mode activated" if self._xyIntegration else "Cross-plot mode activated")
        if self._standAlone:
            self._cursor.set_active(not self._xyIntegration)

        self._updateCrossPlot()

    def update(self):
        """Update the figure.
        """

        # Remove the current image if any
        if self._image:
            self._image.remove()

        self._image = self._mainAxes.imshow(self._dataset[:,:,self._selectedFrame],aspect="auto",origin="lower")

        if self._colorbar is None:
            self._colorbar = self._figure.colorbar(self._image, cax=self._cbarAxes)
            self._colorbar.ax.yaxis.set_ticks_position('left')
                
        plt.draw()

if __name__ == "__main__":

    data = np.random.uniform(0,1,(100,500,40))

    d = DataViewer3D(data)

    plt.show()

                
