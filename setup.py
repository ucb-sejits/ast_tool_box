from setuptools import setup

setup(
    name='ast_tool_box',
    version='1.0.0',

    author="Chick Markley",
    author_email="chickmarkley@gmail.com",

    packages=[
        'ast_tool_box',
        'ast_tool_box.models',
        'ast_tool_box.models.code_models',
        'ast_tool_box.models.transform_models',
        'ast_tool_box.views',
        'ast_tool_box.views.code_views',
        'ast_tool_box.views.transform_views',
        'ast_tool_box.controllers',
        'ast_tool_box.transformers',
    ],

    requires=[
        'PySide (>=1.1.2)',
        'nose',
        'codegen',
        'ctree'
    ],

    entry_points={
        'console_scripts': ['ast_tool_box = ast_tool_box.main:main', ],
    }

)
