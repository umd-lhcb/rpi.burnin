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

    # Code formatter
    black
  ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;
}
