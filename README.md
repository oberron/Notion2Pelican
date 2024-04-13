# Notion2Pelican

Import Notion Pages into a Pelican compatible folder structure and files

> [!IMPORTANT]  
> For this to work you need the ID of your notion database and the key which are available
> from your notion dashboard

1. how to get the ID:
https://docs.tooljet.com/docs/data-sources/notion/#:~:text=Database%20ID%3A%20You'll%20find,ZZZ%20is%20the%20page%20ID.

2. how to get the secret:
https://docs.tooljet.com/docs/data-sources/notion/#:~:text=Database%20ID%3A%20You'll%20find,ZZZ%20is%20the%20page%20ID.

3. Select the page and grant access to the connection (to right ..., select Connections, Connect to, type the name of your integration).

## Examples

See the ./docs folder for minimalist code which imports a Notion DB into a pelican blogging and generates the static site.

> [!IMPORTANT]  
> The below example relies on the secrets to be in a local .env file (which containing secrets has to be created for each machine)
> with the following keys: `FT_dbid` the ID of your database `NOTIONKEY` which usually starts with `secret_` and is available from your 
> Notion dashboard

> cd docs
> python example.py


## Release Notes and Roadmap

v0.0.2 - adding support for

* add support for H1 (which was not present)
* numbered list (which was not working)
* italic and bold (which was not available)
* non regression for images (though it was working)
* add support for quotes

v0.0.1 (first release)

Supports:

* Titles (H1, H2, )
* Bulleted items
* images 

### Upcoming

### Roadmap

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

12. release on pypi (assumes your pypirc is local to the project)
> twine upload -r pypi --config-file=.\.pypirc dist\*

13. check on colab that pypi package works:

>!python -m pip install Notion2Pelican
from Notion2Pelican import __version__
print(__version__)