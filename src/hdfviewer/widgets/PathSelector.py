"""
Adpated from `the following code base <https://stackoverflow.com/questions/48056345/jupyter-lab-browsing-the-remote-file-system-inside-a-notebook>`_
"""

import os

import ipywidgets as widgets

from IPython.display import display


class PathSelector(object):
    """This class allows to create a file browser in the context of **Jupyter Lab**

    :param start_dir: the starting directory for the file browser. If not set, the current working directory will be used.
    :type start_dir: str or None

    :param selectFile: if True the browser is used to select files otherwise it is used as to browse directories.
    :type selectFile: bool

    :param extensions: if set, only those files matching the defined extensions will be displayed otherwise all files are displayed.
    :type extensions: list[int]
    """

    def __init__(self, startingPath=None, selectFile=True, extensions=None):

        self._selectFile = selectFile

        self._select = widgets.SelectMultiple(
            options=[], value=(), rows=10, description='')
        self._widget = widgets.Accordion(children=[self._select])
        self._extensions = extensions if extensions else []
        self._widget.selected_index = None

        self.update(startingPath)

        self._select.observe(self._onUpdate, 'value')

    @property
    def path(self):
        """Return the path selected.

        :return: the selected path
        :rtype: str
        """

        return self._path

    @path.setter
    def path(self, path):

        self._path = path

    @property
    def widget(self):
        """Getter for the file browser widget

        :return: the file browser widget
        :rtype: `ipywidgets.Accordion <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html# Accordion-and-Tab-use-selected_index,-not-value>`_
        """

        return self._widget

    def _onUpdate(self, change):
        """A callable that is called when a new entry of the file browser is clicked

        See `here <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Events.html# Traitlet-events>`__ for more information

        :param change: the state of the traits holder
        :type change: dict
        """

        if len(change['new']) > 0:
            self.update(os.path.join(self._currentDir, change['new'][0]))

    def update(self, path):
        """Update the file browser widget with a new file or directory basename

        This will:

        1. update the name of the current selection on top of the file browser widget
        2. update the directory contents subwidget in case where the new entry is a directory

        :param basename: the new file or directory basename
        :type basename: str
        """

        if path is None:
            path = os.getcwd()

        # Make the path absolute
        path = os.path.abspath(path)

        if not os.path.exists(path):
            return

        self._path = None
        # Case of a file browser
        if self._selectFile:
            if os.path.isfile(path):
                self._path = path
                self._widget.selected_index = None
                self._currentDir = os.path.dirname(path)
                self._widget.set_title(0, path)
            elif os.path.isdir(path):
                self._currentDir = path
            else:
                return
        else:
            self._currentDir = path
            self._widget.set_title(0, path)

        # Build list of files and dirs
        keys = ['[..]']
        for item in os.listdir(self._currentDir):
            if item[0] == '.':
                continue
            elif os.path.isdir(os.path.join(path, item)):
                keys.append('['+item+']')
            else:
                if self._selectFile:
                    if self._extensions:
                        ext = os.path.splitext(item)[-1]
                        if ext in self._extensions:
                            keys.append(item)
                    else:
                        keys.append(item)

        # Sort and create list of output values
        keys.sort(key=str.lower)
        vals = []
        for k in keys:
            if k[0] == '[':
                vals.append(k[1:-1])  # strip off brackets
            else:
                vals.append(k)

        self._select.options = list(zip(keys, vals))
        with self._select.hold_trait_notifications():
            self._select.value = ()
