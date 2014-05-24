reproducible
============

A lightweight tool for simple, efficient, and reproducible scientific modeling.

reproducible will run each step of your code in isolation, saving the data. 
When you re-run your code, a step will only be re-run if its code has been changed or if one of its dependencies has changed.

A few more features will be added eventually.

* A very simple versioning system, where a new results directory is created when the code is changed.
* Pip freeze will be run, creating a requirements.txt, so that the current python environment will be reproducible.
* An option for specifying a code directory will be added. All necessary code will be saved along with the data.
* Specifying one step to be dependent on previous step. If no steps are specified, the step will be assumed to be dependent on all previous steps. A step will only be re-run if it changes or one of its dependencies is re-run.

Setup
-----

To get setup, simply download the code::

  $ git clone https://github.com/tbenthompson/reproducible.git
  
and then run::

  python setup.py install 

I highly recommend installing within a virtualenv instead of in your system site-packages.

Tests
-----

To run the tests, type::

    $ py.test test.py
