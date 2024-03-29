Overview
========
**hdfviewer** is a python3 package for inspecting HDF files in the context of **Jupyter Lab** notebook.

.. overview-begin

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

.. overview-end

Usage in a notebook
===================

.. usage-begin

.. code-block:: python
   :caption: Usage in a notebook

    %matplotlib ipympl

    import h5py
    from hdfviewer.widgets.HDFViewer import HDFViewer
    from hdfviewer.widgets.PathSelector import PathSelector

    path = PathSelector(extensions=[".hdf",".h5",".nxs"])
    path.widget

    if path.file:
        hdf5 = h5py.File(path.file,"r")
        display(HDFViewer(hdf5))

.. usage-end

Prerequesites
=============
- python3 + pip

Installation
============
see `here <https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager>`_ for complementary info

- `cd` to the directory where lies the `setup.py` file
- pip3 install --user .

Troubleshootings
================

You running the widget on JupyterLab you may have get some text describing the widget instead of the actual widget. This means that you may have to install 
the `jupyterlab-manager` and `jupyter-matplotlib` extensions. To check this please run the following command:

- `jupyter labextension list`

If none or only one of these extensions are mentionned, please run the following commands to install the missing one(s):

- `jupyter labextension install @jupyter-widgets/jupyterlab-manager`
- `jupyter labextension install jupyter-matplotlib`


