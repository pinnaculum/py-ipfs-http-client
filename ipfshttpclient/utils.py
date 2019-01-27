"""A module to handle generic operations.
"""

from __future__ import absolute_import

try:
    import collections.abc
except ImportError:
    #PY2: The relevant classes used to be somewhere else
    class collections:
        import collections as abc
import mimetypes
import os
import six
from functools import wraps



path_types = (six.text_type, six.binary_type)
if hasattr(os, "PathLike"):  #PY36+
    path_types += (os.PathLike,)


def guess_mimetype(filename):
    """Guesses the mimetype of a file based on the given ``filename``.

    .. code-block:: python

        >>> guess_mimetype('example.txt')
        'text/plain'
        >>> guess_mimetype('/foo/bar/example')
        'application/octet-stream'

    Parameters
    ----------
    filename : str
        The file name or path for which the mimetype is to be guessed
    """
    fn = os.path.basename(filename)
    return mimetypes.guess_type(fn)[0] or 'application/octet-stream'


def clean_file(file):
    """Returns a tuple containing a ``file``-like object and a close indicator.

    This ensures the given file is opened and keeps track of files that should
    be closed after use (files that were not open prior to this function call).

    Raises
    ------
    OSError : Accessing the given file path failed

    Parameters
    ----------
    file : str | bytes | os.PathLike | io.IOBase | int
        A filepath or ``file``-like object that may or may not need to be
        opened
    """
    if isinstance(file, int):
        return os.fdopen(file, 'rb', closefd=False), True
    elif not hasattr(file, 'read'):
        return open(file, 'rb'), True
    else:
        return file, False


def clean_files(files):
    """Generates tuples with a ``file``-like object and a close indicator.

    This is a generator of tuples, where the first element is the file object
    and the second element is a boolean which is True if this module opened the
    file (and thus should close it).

    Raises
    ------
    OSError : Accessing the given file path failed

    Parameters
    ----------
    files : str | bytes | os.PathLike | io.IOBase | int | collections.abc.Iterable
        Collection or single instance of a filepath and file-like object
    """
    if not isinstance(files, path_types) and not hasattr(files, "read"):
        for f in files:
            yield clean_file(f)
    else:
        yield clean_file(files)


class return_field(object):
    """Decorator that returns the given field of a json response.

    Parameters
    ----------
    field : object
        The response field to be returned for all invocations
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, cmd):
        """Wraps a command so that only a specified field is returned.

        Parameters
        ----------
        cmd : callable
            A command that is intended to be wrapped
        """
        @wraps(cmd)
        def wrapper(*args, **kwargs):
            """Returns the specified field of the command invocation.

            Parameters
            ----------
            args : list
                Positional parameters to pass to the wrapped callable
            kwargs : dict
                Named parameter to pass to the wrapped callable
            """
            res = cmd(*args, **kwargs)
            return res[self.field]
        return wrapper