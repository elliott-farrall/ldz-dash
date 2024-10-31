# LDZ-Dash

## Deployment

The web app has been designed to be easily deployed via [PythonAnywhere](https://eu.pythonanywhere.com) but deployment through other services is also possible. The following is an overview of the steps necessary to deploy the application.

#### Clone the Repository

Start by opening a terminal in the location (henceforth referred to as `<repo>`) where you would like to install the application and run

```bash
git clone https://github.com/ElliottSullingeFarrall/ldz-dash.git
```

to clone the repository. If you don't have enough space to clone the repository, try using the `--depth` option for `git clone`. To select the branch used for the deployment run

```bash
git checkout <branch>
```

where `<branch>` is the name of the branch (e.g: production or testing).

#### Generate the Config File

From the root of the repository, run the `install.sh` script to generate a `.env` file. This file will contain the `SECREY_KEY` variable. Take note of this key as it will be needed throughout the installation process.

**Note:** The `install.sh` requires `poetry` to be installed first.

#### Optional: Create Users

To have some users be created by default, add a file `USERS` in the root of `<repo>` and populate each line with a username.

#### Initialise the Wep App

Next create a web app but don't auto-configure for any frameworks as we will be making use of virtual environments. Make sure the Python version is set to **3.10**.

Set the source to `<repo>/src` and the working directory to `<repo>`. Make sure the `wsgi.py` file looks like

```python
import sys

# add your project directory to the sys.path
project_home = '<repo>/src'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from src import app as application #noqa
```

and the virtual environment is set to `<repo>/.venv`.

#### Setup Auto-Update

The app is configured to automatically pull any changes that are made via a pull request to the `main` branch. To set this up make sure that GitHub has a deployment environment named `<branch>` with the following set:

- A variable `URL` set to the URL of the application.
- A variable `WSGI_PATH` set to the absolute path of the file that starts the web server. When deploying using PythonAnywhere, this path should be given in the web dashboard and will look something like

```
/var/www/<username>_<region>_pythonanywhere_com_wsgi.py
```

- A secret `SECRET_KEY` that is set to the key in the `.env` file generated earlier.

#### First Login

The application should now be operational. For the first login use username and password **default**. It is recommended to create a new admin user as soon as possible and then delete the default user. If you added a `USERS` file these user will also be created with password **default**.

## Development

This project is written using Flask (Python), HTML and CSS. The Python dependencies are managed via Poetry and a development environment is available for Nix users via the `flake.nix`. For non-Nix users, a NixOS devcontainer is also available.

Once all dependencies are installed, run `install.sh` to generate the necessary `.env` file. The web app can be run locally on port 4000 using the `test.sh` script in `wsgi`. This script will automatically restart the app upon any changes to the source code.
