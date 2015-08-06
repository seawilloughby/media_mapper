"""This is the docstring for the example.py module.  Modules names should
have short, all-lowercase names.  The module name may have underscores if
this improves readability.

Every module should have a docstring at the very top of the file.  The
module's docstring may extend over multiple lines.  If your docstring does
extend over multiple lines, the closing three quotation marks must be on
a line by itself, preferably preceeded by a blank line.

"""
# uncomment the following line to use python 3 features
#from __future__ import division, absolute_import, print_function

import shutil
import sys
import os  # standard library imports first

# Do NOT import using *, e.g. from numpy import *
#
# Import the module using


import numpy
import random
#
# instead or import individual functions as needed, e.g
#
#  from numpy import array, zeros
#
# If you prefer the use of abbreviated module names, we suggest the
# convention used by NumPy itself::


# These abbreviated names are not to be used in docstrings; users must
# be able to paste and execute docstrings after importing only the
# numpy module itself, unabbreviated.


def foo(var1, var2, long_var_name='hi'):
    r"""A one-line summary that does not use variable names or the
    function name.

    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
    Long_variable_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    ----------------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Para
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).

    This can have multiple paragraphs.

    You may include some math:

    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

    And even use a greek symbol like :math:`omega` inline.

    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.

    .. [1] O. McNoleg, "The integration of GIS, remote sensing,
       expert systems and adaptive co-kriging for environmental habitat
       modelling of the Highland Haggis using object-oriented, fuzzy-logic
       and neural-network techniques," Computers & Geosciences, vol. 22,
       pp. 585-588, 1996.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> a=[1,2,3]
    >>> print [x + 3 for x in a]
    [4, 5, 6]
    >>> print "a\n\nb"
    a
    b

    """

    pass

# python functions are very flexable


def simple_function(x, y=3, letter='b', tf=True, none=None, *args, **kwargs):
    '''also comments are cool! try tabbing in ipyhton to see
    what a comment in a function says'''
    print 'x = ' + str(x)
    print 'x*y = ' + str(x * y)
    print 'the letter is: ' + letter
    if tf:
        print 'the boolean variable is True :-)'
    else:
        print 'the boolean variable is was not True :-('
    if none is not None:
        print 'none is not None'
        print 'none is : ' + str(none)
    print "also...."
    print args
    print kwargs
    return x * y

# classes are also easy to build


class Die:
    #     first every class needs an __init__ method
    #     __init__ gets run automatically when you instantiate an object

    def __init__(self, sides=6):
        '''die represents a single die with the property of sides and the methods of roll and rolln'''
        self.sides = sides

    def roll(self):
        self.rolled = random.randint(1, self.sides)
        print self.rolled

    def rolln(self, n=10):
        self.rolled = [random.randint(1, self.sides) for x in range(n)]
        print self.rolled


class GeneralClass:

    '''GeneralClass provides a simple interface for initalizing arguments passed in kwargs
    and a runMethod method for running a class method by name'''

    def __init__(self, **kwargs):
        self.set_attributes(kwargs)

    def set_attributes(self, kwargs):
        '''
        Initalizes the given argument structure as properties of the class
        to be used by name in specific method execution.

        Parameters
        ----------
        kwargs : dictionary
            Dictionary of extra attributes,
            where keys are attributes names and values attributes values.

        '''
        for key, value in kwargs.items():
            setattr(self, key, value)
            # print key, value

    def run_method(self, method):
        '''call a specied method by name using runMethod'''
        methodToCall = getattr(self, method)
        result = methodToCall()

if __name__ == '__main__':
    z = simple_function(x=1, none=15)
    # instantiate the object 'myDie', overriding the default #sides
    my_die = Die(24)

    # run the 'roll' function under the object which rolls and prints result
    my_die.roll()
    # run the 'rolln' function under the object which rolls n times and prints
    # results
    my_die.rolln(5)

    # make a general object
    obj = GeneralClass(param1=1, x=1, z=3, milkBone='MMMM thats good stuff')
    print obj.argList
