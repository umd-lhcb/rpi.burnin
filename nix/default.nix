{ stdenv
, buildPythonPackage
, RPi_GPIO
, fake_rpi
, hidapi
}:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3.5";

  src = builtins.path { path = ./..; name = pname; };

  propagatedBuildInputs = [ hidapi ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  doCheck = false;
}
