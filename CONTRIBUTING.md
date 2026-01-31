## Setup venv
The development is being done in the lowest supported Python version.  
The list of the supported Python versions can be found in `tox.ini`.


```bash
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

## Lint
#### The lint execution (as in CI/CD):
```bash
tox -e lint
```

#### The lint fixing and formatting:
```bash
ruff format
ruff check --fix
```

I recommend to repeat the fixing and formatting several times (2-3 times) in a row,  
since after the formatting ruff does not add trailing commas, then with `check --fix` it adds commas,  
then with the trailing commas it formats in a different way, and so on.  
  
Not all lint violations can be fixed automatically. Something can be fixed only by hands.

## Test regression execution
For the tests execution all supported Python versions must be installed in your OS.  
The list of the supported Python versions can be found in `tox.ini`.  
  
Tests execution (as in CI/CD):
```bash
tox
```