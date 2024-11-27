{ mkShell
, pkgs
, inputs
, system
, ...
}:

mkShell {
  name = "python";

  buildInputs = inputs.self.checks.${system}.pre-commit.enabledPackages;
  packages = with pkgs; [
    python310
    poetry
    ruff

    inotify-tools
    openssl
    (uwsgi.override { python3 = python310; plugins = [ "python3" ]; })

    zip
  ];

  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

  POETRY_VIRTUALENVS_IN_PROJECT = true;
  shellHook = ''
    poetry env use $(which python)
    poetry install
  '' + inputs.self.checks.${system}.pre-commit.shellHook;
}
