AstToolBox
==========

The AstToolBox allows a developer to start from a python source file and
see how a series of ast.NodeTransformers change it, and how a CodeGenerator
will render the AST at any given point.

Files and transforms can be reloaded at any time which facilitates development.
If a tree does not look right after some transformation, the transform can be
edited and reloaded and reapplied.

This tool was derived from `AstViewer <https://github.com/titusjan/astviewer>`_

.. image:: screen_shot.png

Usage:
======
*	Command line example:
	
		%> ast_tool_box myprog.py
	
*	Examples to use from within Python:

	```python
	>>> from astviewer import view
	>>> view(file_name='myprog.py', width=800, height=600)
	>>> view(source_code = 'a + 3', mode='eval')
	```

#### Further links:

The `Green Tree Snakes documentation on ASTs <http://greentreesnakes.readthedocs.org/>`_ is available
for those who find the `Python ast module documentation <http://docs.python.org/3/library/ast>`_ too brief.

Installation:
=============
1.	Install PySide:
	`<http://qt-project.org/wiki/Category:LanguageBindings::PySide>`_

2.	Run the installer:

		%> python setup.py install

