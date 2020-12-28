{
  description = "This library provides an interface from the various Raspberry Pi models for burn-in related activities.";

  inputs = rec {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-20.09";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    {
      overlay = import ./nix/overlay.nix;
    }
    //
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
        python = pkgs.python3;
        pythonPackages = python.pkgs;
        stdenv = pkgs.stdenv;
      in
      {
        devShell = pkgs.mkShell {
          name = "rpi.burnin";
          buildInputs = with pythonPackages; [
            pkgs.pythonPackages.rpi_burnin
          ]
          ++ stdenv.lib.optionals (stdenv.isx86_64) [
            # Python auto-complete
            jedi

            # Linters
            flake8
            pylint
          ];
        };
      });
}
