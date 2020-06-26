let
  pkgs = import <nixpkgs> { overlays = [(import ./nix/burnin)]; };
  python = pkgs.python3;
  pythonPackages = python.pkgs;
  stdenv = pkgs.stdenv;
in

pkgs.mkShell {
  name = "rpi.burnin";
  buildInputs = with pythonPackages; [
    # Compilers and other build dependencies
    stdenv

    # Some Python libraries needs to be installed via nix
    hidapi

    # Python requirements (enough to get a virtualenv going).
    virtualenvwrapper
  ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  shellHook = ''
    # Allow the use of wheels.
    SOURCE_DATE_EPOCH=$(date +%s)

    if test -d $HOME/build/python-venv; then
      VENV=$HOME/build/python-venv/rpi.burnin
    else
      VENV=./.virtualenv
    fi

    if test ! -d $VENV; then
      virtualenv $VENV
    fi
    source $VENV/bin/activate

    # allow for the environment to pick up packages installed with virtualenv
    export PYTHONPATH=$VENV/${python.sitePackages}/:$PYTHONPATH
  '';
}
