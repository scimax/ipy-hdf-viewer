import binascii
import io
import json
import os
import webbrowser

import numpy as np

import h5py

import matplotlib.pyplot as plt

import ipywidgets as widgets

from IPython.core.display import display

from hdfviewer import __version__
from hdfviewer.viewers.MplDataViewer import MplDataViewer, MplDataViewerError
from hdfviewer.widgets.MplOutput import MplOutput


class HDFViewerError(Exception):
    """Error handler for :mod:`HDFViewer` related exceptions.
    """

    pass


def _openHDFFile(filename):
    """Open a HDF file.

    The file can be a *true* HDF file or a json file in which a HDF has been dumped into.

    :param hdfSource: the path to the file storing the HDF contents
    :type hdfSource: str

    The file can be a path to a *true* HDF file or to a file in which the HDF contents has been dumped into.
    :raises: :class:`TypeError` if the input is not a str
    :raises: :class:`IOError` if the path is not valid or could not be opened through :mod:`h5py` API
    """

    hdf = None
    if not isinstance(filename, str):
        raise TypeError("invalid input type")

    if not os.path.isfile(filename):
        raise IOError("the input is not a file")

    # First try to open the file as a HDF5 file
    try:
        hdf = h5py.File(filename, "r")
    # Any exception should be caught at this level
    except:
        # Try to open it as a json dumped HDF file
        # The JSON must contain the str version
        with open(filename, "r") as f:

            d = json.load(f)
            byt = binascii.a2b_base64(d["data"])

            try:
                hdf = h5py.File(io.BytesIO(byt), "r")
            # Any exception should be caught at this level
            except:
                pass
    finally:
        return hdf


def HDFViewerWidget(filename, startingPath=None):
    """Helper function that displays a :class:`HDFViewer` widget from a file.

    The file can be a *true* HDF file or a json file in which a HDF has been dumped into.

    :param hdf: the path to the file storing the HDF contents
    :type hdf: str
    :param startPath: the hdf path from where the HDF data will be inspected.

        If not set, the starting path will be the root of the HDF data
    :type startPath: str or None
    """

    vbox = widgets.VBox()

    button = widgets.Button(description="documentation",
                            tooltip="open documentation for release {0}".format(__version__))

    button.on_click(lambda event: HDFViewer.info())

    hdf = _openHDFFile(filename)
    if hdf is None:
        raise HDFViewerError(
            "An error occured when reading {!r} file".format(filename))

    vbox.children = [button, HDFViewer(hdf, startingPath)]

    return vbox


class HDFViewer(widgets.Accordion):
    """This class allows to inspect HDF data in the context of **Jupyter Lab**

    .. include:: ../README.rst
       :start-after: overview-begin
       :end-before: overview-end

    .. include:: ../README.rst
       :start-after: usage-begin
       :end-before: usage-end

    :param hdf: the hdf data file to be inspected.
    :type hdf: :class:`h5py.File`
    :param startPath: the hdf path from where the HDF data will be inspected.

        If not set, the starting path will be the root of the HDF data
    :type startPath: str or None
    """

    def __init__(self, hdf, startPath=None):

        widgets.Accordion.__init__(self)

        self._hdf = hdf

        if startPath is None:
            self._startPath = "/"
            self.children = [HDFViewer(self._hdf, self._startPath)]
            self.set_title(0, self._startPath)
        else:
            self._startPath = startPath

            attributesAccordion = widgets.Accordion()
            for idx, (key, value) in enumerate(self._hdf[self._startPath].attrs.items()):
                attributesAccordion.children = list(
                    attributesAccordion.children) + [widgets.HTML(value)]
                attributesAccordion.set_title(idx, key)

            # Setup the groups and datasets accordion
            groupsAccordion = widgets.Accordion()
            datasetsAccordion = widgets.Accordion()
            for value in list(self._hdf[self._startPath].values()):
                if isinstance(value, h5py.Group):
                    groupsAccordion.children = list(
                        groupsAccordion.children) + [HDFViewer(hdf, value.name)]
                    groupsAccordion.set_title(
                        len(groupsAccordion.children)-1, value.name)
                elif isinstance(value, h5py.Dataset):
                    datasetInfo = []
                    shape = value.shape
                    # Set some informations about the current hdf value
                    datasetInfo.append("<i>Dimension: %s</i>" % str(shape))
                    datasetInfo.append("<i>Reduced dimension: %s</i>" %
                                       str(tuple([s for s in shape if s != 1])))
                    datasetInfo.append("<i>Type: %s</i>" % value.dtype.name)
                    datasetInfo = "<br>".join(datasetInfo)
                    vbox = widgets.VBox()
                    vbox.children = [widgets.HTML(datasetInfo), MplOutput()]
                    datasetsAccordion.children = list(
                        datasetsAccordion.children) + [vbox]
                    datasetsAccordion.set_title(
                        len(datasetsAccordion.children)-1, value.name)
                    datasetsAccordion.observe(
                        self._onSelectDataset, names="selected_index")

            # Display only the accordions which have children
            nestedAccordions = [("attributes", attributesAccordion),
                                ("groups", groupsAccordion), ("datasets", datasetsAccordion)]
            for title, acc in nestedAccordions:
                if not acc.children:
                    continue
                acc.selected_index = None
                self.children = list(self.children) + [acc]
                self.set_title(len(self.children)-1, title)

        # By default, the accordion is closed at start-up
        self.selected_index = None

    def _onSelectDataset(self, change):
        """A callable that is called when a new dataset is selected

        See `here <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Events.html#Traitlet-events>`__ for more information

        :param change: the state of the traits holder
        :type change: dict
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
                self._viewer = MplDataViewer(self._hdf[path], standAlone=False)
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
        url = os.path.join(
            "https://hdf-viewer.readthedocs.io/en/{0}".format(version))
        webbrowser.open(url)
