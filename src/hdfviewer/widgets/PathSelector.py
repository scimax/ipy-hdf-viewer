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

    def __init__(self,startDir=None,selectFile=True,extensions=None):        

        self._file  = None 
        self._selectFile = selectFile
        self._startDir = startDir if startDir else os.environ["HOME"]
        self._select = widgets.SelectMultiple(options=['init'],value=(),rows=10,description='') 
        self._widget = widgets.Accordion(children=[self._select])        
        self._extensions = extensions if extensions else []

        # Start closed (showing path only)
        self._widget.selected_index = None
        self.update(self._startDir)
        self._select.observe(self._onUpdate,'value')

    @property
    def file(self):
        """Return the path selected.

        :return: the selected path
        :rtype: str
        """

        return self._file

    @property
    def widget(self):
        """Getter for the file browser widget

        :return: the file browser widget
        :rtype: `ipywidgets.Accordion <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html#Accordion-and-Tab-use-selected_index,-not-value>`_
        """

        return self._widget

    def _onUpdate(self,change):
        """A callable that is called when a new entry of the file browser is clicked

        See `here <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Events.html#Traitlet-events>`_ for more information
        """

        if len(change['new']) > 0:
            self.update(change['new'][0])

    def update(self,item):
        """Update the file browser widget with a new entry (file or directory name)

        This will:

        1. update the name of the current selection on top of the file browser widget
        2. update the directory contents subwidget in case where the new entry is a directory

        :param entry: the filename or directory name to update the file browser with
        :type entry: str
        """

        path = os.path.abspath(os.path.join(self._startDir,item))

        if os.path.isfile(path):
            if self._selectFile:
                self._widget.set_title(0,path)  
                self._file = path
                self._widget.selected_index = None
            else:
                self._select.value = ()
        else: 
            self._file = None 
            self._startDir  = path

            # Build list of files and dirs
            keys = ['[..]']; 
            for item in os.listdir(path):
                if item[0] == '.':
                    continue
                elif os.path.isdir(os.path.join(path,item)):
                    keys.append('['+item+']'); 
                else:
                    if self._extensions:
                        ext = os.path.splitext(item)[-1]
                        if ext in self._extensions:
                            keys.append(item); 
                    else:
                        keys.append(item); 

            # Sort and create list of output values
            keys.sort(key=str.lower)
            vals = []
            for k in keys:
                if k[0] == '[':
                    vals.append(k[1:-1]) # strip off brackets
                else:
                    vals.append(k)

            # Update widget
            self._widget.set_title(0,path)  
            self._select.options = list(zip(keys,vals)) 
            with self._select.hold_trait_notifications():
                self._select.value = ()
