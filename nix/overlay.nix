final: prev:
let
  pythonOverrides = {
    packageOverrides = self: super: {
      build_utils = super.callPackage ./build_utils { };
      RPi_GPIO = super.callPackage ./RPi.GPIO { };
      fake_rpi = super.callPackage ./fake_rpi { };
      rpi_burnin = super.callPackage ./default.nix { };
    };
  };
in
rec {
  python3 = prev.python3.override pythonOverrides;
  pythonPackages = python3.pkgs;
}
