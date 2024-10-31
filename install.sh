export POETRY_VIRTUALENVS_IN_PROJECT=true

poetry env use $(which python)
poetry install

if [ ! -f .env ]; then
  touch .env
  random_key=$(openssl rand -base64 32)
  echo "SECRET_KEY = '$random_key'" >>.env
fi
