Versioning
====================================================================================================

### Prerequisites
* git tag

```sh	
git tag -a v0.1.0 -m "0.1.0"
```

* versioneer install

```sh	
pip install git+https://github.com/warner/python-versioneer.git
```

### running versioneer

follow the instructions for versioneer: https://github.com/warner/python-versioneer

navigate to the root directory folder and run:

```sh
versioneer install
```


### tagging git version

```sh
git tag -a v1.0.0 -m "version 1.0.0"
git push --tags
```

### removing local and remote git tags
	
```sh
cp scripts/rm_git_tags.sh rm_git_tags.sh
sh rm_git_tags.sh
```

### deploying to PiPy

https://python-packaging-user-guide.readthedocs.org/en/latest/distributing.html

```sh
sudo python setup.py install
sudo python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*
```