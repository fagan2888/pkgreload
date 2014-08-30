"""
Method for reloading a package recursively.
"""

# future imports
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

# global imports
import os
import re
import importlib

# exported symbols
__all__ = ['pkgreload']


def _find_modules(path):
    """
    Given a filepath iterate over all python modules located under that path.
    Return a tuple include the file name, the module name, and a boolean
    indicating whether the module is a package.
    """
    for (root, _, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith('.py'):
                ispackage = filename.endswith('__init__.py')
                fname = os.path.join(root, filename)
                mname = fname[:(-12 if ispackage else -3)].replace('/', '.')
                yield fname, mname, ispackage


def _toposort(graph):
    """
    Perform a topological sort of the given graph, where the graph should be
    given as a dictionary of items mapping to sets of children. Returns an
    iterator over the elements.

    Code initially based on:
    http://code.activestate.com/recipes/578272-topological-sort/
    """
    # Ignore self dependencies (this also makes a copy of the graph).
    graph = {k: v-{k} for (k, v) in graph.iteritems()}

    # Find any items that are dependencies, but do not have a node in the graph
    # (ie they aren't a dictionary key) and add them in.
    nodeps = {i for s in graph.itervalues() for i in s} - set(graph.iterkeys())
    graph.update({i: set() for i in nodeps})

    while True:
        # find nodes that have no dependencies and iterate over them (breaking
        # out of the loop if none exist).
        nodeps = set(i for (i, deps) in graph.iteritems() if not deps)

        if not nodeps:
            break

        for item in nodeps:
            yield item

        # update the graph by removing the nodes in nodeps.
        graph = {i: (deps - nodeps)
                 for (i, deps) in graph.iteritems() if i not in nodeps}

    if len(graph) > 0:
        raise ValueError('Cyclic dependencies exist between: ' +
                         ', '.join(repr(x) for x in graph.iteritems()))


def pkgreload(module):
    """
    Reload the given module and all of its submodules.
    """
    module = reload(module)
    if not hasattr(module, '__path__'):
        return

    # get all the files as a tuple of file name, module name, and a boolean
    # representing whether the module is a package.
    files = list(_find_modules(module.__path__[0]))

    # make a dictionary mapping each module to a set containing the modules
    # that it imports from.
    modules = {mname: set() for (_, mname, _) in files}

    # regular expression matching import statements.
    local_imports = re.compile(r'\s*from (\..*) import (.+)\s*')

    for (fname, mname, ispackage) in files:
        path = mname.split('.')

        for rel, imports in local_imports.findall(open(fname).read()):
            mod = rel.lstrip('.')
            num = len(rel) - len(mod) - (1 if ispackage else 0)
            mod = \
                mname if (num == 0) else '.'.join(path[:-num]) + \
                ('.' + mod) if mod else ''

            # get all the full imports.
            imports = [mod + '.' + _ for _ in imports.split(', ')]

            modules[mname].update([_ for _ in imports if _ in modules])
            modules[mname].update([_ for _ in [mod] if _ is not mname])

    for module in _toposort(modules):
        print("Reloading '%s'" % module)
        reload(importlib.import_module(module))

