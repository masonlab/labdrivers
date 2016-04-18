##############
Installation
##############

There are a couple ways to install labdrivers.

Installing to the system Python Folder
--------------------------------------

To install labdrivers to the default Python installation you
can use `pip`::

    > pip install git+https://github.com/masonlab/labdrivers.git

Installing to a Conda Environment
---------------------------------

If you are comofortable using `conda` environments you can use
`conda` to download all the required dependencies and set up an environment::

    > git clone https://github.com/masonlab/labdrivers
    > cd labdrivers
    > conda env create

The included `environment.yml` will 
create a conda environment named `labdrivers` and install all
the necessary dependencies. Activate the environment
and start a Juypter notebook server with::

    > source activate labdrivers          (on linux)
    > activate labdrivers                 (on windows)
    > jupyter notebook


