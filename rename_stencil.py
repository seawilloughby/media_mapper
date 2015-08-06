
# coding: utf-8

# In[1]:

'''Use this script to scan your current path and 
all sub folders to change all instances of the 
word media_mapper to the name of the top level folder'''


# import relpy as rp
import os
import sys

import fnmatch


# In[2]:

def replace_text_in_files(files, old, new ):
    for f in files:
        print 'Renamed: '+f
        with open (f, "r+") as myfile:
            data = myfile.read().replace(old, new)
            myfile.truncate()
	open(f, 'w').close()
	with open(f, "w") as myfile:
            myfile.seek(0)
            myfile.write(data)
            
def Walk(root='.', recurse=True, pattern='*'):
    """
        Generator for walking a directory tree.
        Starts at specified root folder, returning files
        that match our pattern. Optionally will also
        recurse through sub-folders.

        Parameters
        ----------
        root : string (default is *'.'*)
            Path for the root folder to look in.
        recurse : bool (default is *True*)
            If *True*, will also look in the subfolders.
        pattern : string (default is :emphasis:`'*'`, which means all the files are concerned)
            The pattern to look for in the files' name.

        Returns
        -------
        generator
            **Walk** yields a generator from the matching files paths.

    """
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path, name)
        if not recurse:
            break


def scan_path(root='.', recurse=False, pattern='*'):
    '''
    Runs a loop over the :doc:`Walk<relpy.utils.Walk>` Generator
    to find all file paths in the root directory with the given
    pattern. If recurse is *True*: matching paths are identified
    for all sub directories.

    Parameters
    ----------
    root : string (default is *'.'*)
        Path for the root folder to look in.
    recurse : bool (default is *True*)
        If *True*, will also look in the subfolders.
    pattern : string (default is :emphasis:`'*'`, which means all the files are concerned)
        The pattern to look for in the files' name.

    Returns
    -------
    pathList : list
        The list of all the matching files paths.

    '''

    pathList = []
    for path in Walk(root=root, recurse=recurse, pattern=pattern):
        pathList.append(path)
    return pathList


# In[4]:

def main():
    old = 'media_mapper'
    new = os.path.realpath('./').split('/')[-1]
    
    files = scan_path(root = './', recurse=True, pattern = '*.py')
    replace_text_in_files(files, old, new)
    
    files = scan_path(root = './', recurse=True, pattern = '*.in')
    replace_text_in_files(files, old, new)
    
    files = scan_path(root = './', recurse=True, pattern = '*.cfg')
    replace_text_in_files(files, old, new)
    

    files = scan_path(root = './', recurse=True, pattern = '*.md')
    replace_text_in_files(files, old, new)

    #rename sub folder
    os.rename('./'+old, './'+new)


# In[36]:

if __name__=='__main__':
    main()

