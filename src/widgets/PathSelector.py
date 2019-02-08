"""
Code taken and slightly modified from https://stackoverflow.com/questions/48056345/jupyter-lab-browsing-the-remote-file-system-inside-a-notebook
"""

import sys
import os
import ipywidgets as widgets

from IPython.display import display

class PathSelector(object):

    def __init__(self,start_dir=None,select_file=True,extensions=None):        
        self.file        = None 
        self.select_file = select_file
        self.cwd         = start_dir if start_dir else os.environ["HOME"]
        self.select      = widgets.SelectMultiple(options=['init'],value=(),rows=10,description='') 
        self.widget      = widgets.Accordion(children=[self.select])        
        self.extensions = extensions if extensions else []

        self.widget.selected_index = None # Start closed (showing path only)
        self.refresh(self.cwd)
        self.select.observe(self.on_update,'value')

    def on_update(self,change):
        if len(change['new']) > 0:
            self.refresh(change['new'][0])

    def refresh(self,item):
        path = os.path.abspath(os.path.join(self.cwd,item))

        if os.path.isfile(path):
            if self.select_file:
                self.widget.set_title(0,path)  
                self.file = path
                self.widget.selected_index = None
            else:
                self.select.value = ()

        else: # os.path.isdir(path)
            self.file = None 
            self.cwd  = path

            # Build list of files and dirs
            keys = ['[..]']; 
            for item in os.listdir(path):
                if item[0] == '.':
                    continue
                elif os.path.isdir(os.path.join(path,item)):
                    keys.append('['+item+']'); 
                else:
                    if self.extensions:
                        ext = os.path.splitext(item)[-1]
                        if ext in self.extensions:
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
            self.widget.set_title(0,path)  
            self.select.options = list(zip(keys,vals)) 
            with self.select.hold_trait_notifications():
                self.select.value = ()
