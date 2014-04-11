from distutils.core import setup

setup(
    name='ast_tool_box',
    version='1.0.0',
    author="Chick Markley",
    author_email="chickmarkley@gmail.com",
    py_modules=['ast_viewer'],
    scripts=['ast_tool_box'],
    requires=[
        'PySide (>=1.1.2)',
        'nose',
    ],
)
