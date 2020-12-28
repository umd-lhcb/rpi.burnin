{ stdenv
, buildPythonPackage
, fetchPypi
, numpy
, build_utils
}:

buildPythonPackage rec {
  pname = "fake_rpi";
  version = "0.6.2";

  src = fetchPypi {
    inherit pname version;
    extension = "tar.gz";
    sha256 = "1d129295047d723b363bdd8cd31592229c5c3b9560dd8f92360597aae468552d";
  };

  # The tarball on PyPI doesn't contain README file!
  preBuild = ''
    echo "Long description" > readme.md
  '';

  buildInputs = [
    build_utils
  ];

  propagatedBuildInputs = [
    numpy
  ];

  # No check avaliable
  doCheck = false;
}
