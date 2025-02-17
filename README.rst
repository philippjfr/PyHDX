=====
PyHDX
=====

|biorxiv| |test_action| |zenodo| |license| |docs| |coverage|

.. |zenodo| image:: https://zenodo.org/badge/206772076.svg
   :target: https://zenodo.org/badge/latestdoi/206772076

.. |biorxiv| image:: https://img.shields.io/badge/bioRxiv-v2-%23be2635
   :target: https://www.biorxiv.org/content/10.1101/2020.09.30.320887v2
   
.. |license| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT

.. |test_action| image:: https://github.com/Jhsmit/PyHDX/workflows/pytest/badge.svg
    :target: https://github.com/Jhsmit/PyHDX/actions?query=workflow%3Apytest
    
.. |docs| image:: https://readthedocs.org/projects/pyhdx/badge/?version=latest
    :target: https://pyhdx.readthedocs.io/en/latest/?badge=latest

.. |coverage| image:: https://codecov.io/gh/Jhsmit/PyHDX/branch/master/graph/badge.svg?token=PUQAEMAUHH
      :target: https://codecov.io/gh/Jhsmit/PyHDX
    

`PyHDX stable documentation <https://pyhdx.readthedocs.io/en/stable/>`_

.. raw:: html

    <img src="images/screenshot_pyhdx040b5.png" width="1000" />


PyHDX is python project which can be used to derive Gibbs free energy from HDX-MS data.
Currently version 0.3.2 is the stable release. Version 0.4.0 is released as beta.

Installation 
============

Installation of the latest stable beta with `pip`:

.. code-block:: console

    pip install pyhdx==0.4.0b8

Installation with web interface extra:

.. code-block:: console

    pip install pyhdx==0.4.0b8[web]


Run PyHDX
=========

Most up-to-date code examples are in the directory `pyhdx/templates`

To run the web server:

.. code-block:: console

    pyhdx serve
    
Please refer to the `docs <https://pyhdx.readthedocs.io/en/stable/>`_ for more details on how to run PyHDX.


Web Application
===============

The PyHDX web application is currently hosted at:
http://pyhdx.jhsmit.org/main

A test file can be downloaded from `here <https://raw.githubusercontent.com/Jhsmit/PyHDX/master/tests/test_data/input/ecSecB_apo.csv>`_ and `here <https://raw.githubusercontent.com/Jhsmit/PyHDX/master/tests/test_data/input/ecSecB_dimer.csv>`_. (right click, save as).

The 0.4.0b4 version of PyHDX (featuring batch fitting / multiple states) is hosted at:
http://pyhdx-beta.jhsmit.org/main

The latest beta docs are found `here <https://pyhdx.readthedocs.io/en/latest/>`_

Publication
===========

Our Analytical Chemistry Publication describing PyHDX can be found here: https://doi.org/10.1021/acs.analchem.1c02155

The latest version (v2) of our biorxiv paper: https://doi.org/10.1101/2020.09.30.320887 

Python code for analysis and generation the figures in the paper are here: https://github.com/Jhsmit/PyHDX-paper

