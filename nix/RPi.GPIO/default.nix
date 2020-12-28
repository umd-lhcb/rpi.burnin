{ stdenv, buildPythonPackage, fetchPypi }:

buildPythonPackage rec {
  pname = "RPi.GPIO";
  version = "0.7.0";

  src = fetchPypi {
    inherit pname version;
    extension = "tar.gz";
    sha256 = "7424bc6c205466764f30f666c18187a0824077daf20b295c42f08aea2cb87d3f";
  };

  # No check avaliable
  doCheck = false;
}
