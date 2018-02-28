NTA Database Library
====================

|docs|

This repository contains a Python library to facilitate working with the nta database in https://www.github.com/CN-TU/nta-meta-analysis

Install
=======

The following instructions will download the latest version of this repository and allow you to use it.

1. Clone the repository to your local machine:

.. code-block:: bash

    $ git clone https://github.com/CN-TU/nta-meta-analysis-library.git
    
2. Update the specification files to the latest version:

.. code-block:: bash

    $ cd nta-meta-analysis-library && ./configure.sh
    
Updating to latest version
--------------------------

To update the specification files, simply run ``./configure.sh`` again.

Included scripts
================

At the moment the only included script (``list_field.py``) lists the existing values in the database for a specific field.
This is its usage:

.. code-block:: bash
    
    usage: list_field.py [-h] [--per-paper] [--papers] [-F SEP] database field

optional arguments:
  -h, --help         show this help message and exit
  --per-paper        With this option, each duplicated values in the same
                     paper are counted only once.
  --papers           With this option, get the papers that use each value.
  -F SEP, --sep SEP  Separator to use in the output.
  
Example usage:

.. code-block:: bash

    $ python list_field.py ../nta-meta-analysis/v2_papers/ reference.authors.author --papers



About the project
=================

This repository contains work performed by the Communications Network Group at TU Wien, Institute of Telecommunications.

More information about this work can be found here: https://www.cn.tuwien.ac.at/network-traffic/ntadatabase/

Additionally, documentation for this repository can be found here: https://nta-meta-analysis.readthedocs.io/en/latest/

.. |docs| image:: https://readthedocs.org/projects/nta-meta-analysis/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://nta-meta-analysis.readthedocs.io/en/latest/?badge=latest
