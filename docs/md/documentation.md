Documentation
====================================================================================================

### Prerequisites
* sphinx
* sphinx-pypi-upload


### Make Documentation

navigate to the docs folder and run the make.py file

	cd docs
	python make.py


once the documentation is built, the index.html file will live in docs/build/html


### Upload Documentation

If you are using PiPy to host your package the documentation can be auto-uploaded

https://pythonhosted.org/an_example_pypi_project/buildanduploadsphinx.html

from the top of the package path:

	easy_install sphinx-pypi-upload
	python setup.py upload_sphinx
