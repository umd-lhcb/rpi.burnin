let
  pythonPackageOverlay = overlay: attr: self: super: {
    ${attr} = self.lib.fix (py:
      super.${attr}.override (old: {
        self = py;
        packageOverrides = self.lib.composeExtensions
          (old.packageOverrides or (_: _: { }))
          overlay;
      }));
  };
in
pythonPackageOverlay
  (self: super: {
    build_utils = super.callPackage ./build_utils { };
    RPi_GPIO = super.callPackage ./RPi.GPIO { };
    fake_rpi = super.callPackage ./fake_rpi { };
    rpi_burnin = super.callPackage ./default.nix { };
  }) "python3"
