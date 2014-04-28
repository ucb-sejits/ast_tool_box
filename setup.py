from distutils.core import setup

setup(
    name='ast_tool_box',
    version='1.0.0',

    author="Chick Markley",
    author_email="chickmarkley@gmail.com",
    py_modules=['ast_viewer'],

    packages=[
        'ast_viewer',
        'ast_viewer.models',
        'ast_viewer.views',
        'ast_viewer.controllers',
        'ast_viewer.transformers',
    ],

    scripts=['ast_tool_box'],

    requires=[
        'PySide (>=1.1.2)',
        'nose',
        'codegen'
    ],

    entry_points={
        'console_scripts': ['ast_tool_box = ast_viewer.ast_toolbox:main'],
    }

)
