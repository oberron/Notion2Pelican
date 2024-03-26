# Notion2Pelican

Import Notion Pages into a Pelican compatible folder structure and files

## Release Notes and Roadmap

## Release process

1. run pyroma
(should be 10/10)

> pyroma .

2. run flake8 
runs with darglint settings for docstrings to numpy standard set in the .flake8 file
should yield 0 warnings or errors

> flake8

3. run pytest
should yield 100% pass

> pytest

4. run coverage

> coverage run -m pytest

5. run coverage report
(should be 100%)

> coverage report

6. run tox

7.run sphinx-api 
`updates the *.rst in docs/ folder`

> sphinx-apidoc -f -o docs Notion2Pelican

8. run sphinx-build
(updates the read_the_docs folder)

> sphinx-build -b html docs build/html

9. release to pypi-test

> python setup.py bdist_wheel

> twine upload -r testpypi dist\*

10. check updates on read_the_docs

11. check on google colab it works

12. release on pypi
> twine upload -r pypi dist\*

13. check on colab that pypi package works:

>!python -m pip install Notion2Pelican
from Notion2Pelican import __version__
print(__version__)