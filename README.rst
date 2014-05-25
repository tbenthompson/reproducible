reproducible
============

A lightweight tool for simple, efficient, and reproducible scientific modeling.

reproducible will run each step of your code in isolation, saving the data. 
When you re-run your code, a step will only be re-run if its code has been changed or if one of its dependencies has changed.
Additionally, there is a very simple versioning system. A new results directory is created when the code is changed.
Using a configuration, pip freeze can be run, creating a requirements.txt. The result is that the current python environment will be reproducible.

A few more features will be added eventually.

* An option for specifying a code directory will be added. All necessary code will be saved along with the data.
* Specifying one step to be dependent on previous step. If no steps are specified, the step will be assumed to be dependent on all previous steps. A step will only be re-run if it changes or one of its dependencies is re-run.

Qualifications.

* In order to use reproducible, all the objects you wish to save must be python picklable.

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
