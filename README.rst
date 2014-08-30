=========
pkgreload
=========

Simple implementation of a function `pkgreload` which will reload a python
package and all of its submodules in the correct order. This is not designed to
work in every instance, however, and if you do anything exotic with the modules
aside from just `from foo import bar` or `import bar` then it will probably
break.

