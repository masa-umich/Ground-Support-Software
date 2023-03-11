
# Getting Started

```commandline
python --version
```

If you don't have 3.11 installed, you're a satanist. Install 3.11.

```commandline
pip --version
```

If this isn't pip for 3.11, see above. Then, 

```commandline
pip install poetry
```

Then, in the root level of the repo, run

```commandline
poetry install
```

Then, open two terminals and start virtual environments:

```commandline
poetry shell
```

Then, cd into the `Python` directory and run

```commandline
python server.py
```

To start the server in one shell, and run

```commandline
python gui.py
```

To start the GUI in another