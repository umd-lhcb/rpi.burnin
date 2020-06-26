self: super:

let
  pythonOverrides = {
    packageOverrides = self: super: {
      build_utils = super.callPackage ./build_utils {};
      RPi_GPIO = super.callPackage ./RPi.GPIO {};
      fake_rpi = super.callPackage ./fake_rpi {};
    };
  };
in

{
  python3 = super.python3.override pythonOverrides;
}
