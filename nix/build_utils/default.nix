{ stdenv
, buildPythonPackage
, fetchPypi
, nose
, twine
, colorama
}:

buildPythonPackage rec {
  pname = "build_utils";
  version = "0.3.2";

  src = fetchPypi {
    inherit pname version;
    extension = "tar.gz";
    sha256 = "9ac4e66f8b18376dc457912ef4355805824aa751d21408594ea77d81a9ae396b";
  };

  # The tarball on PyPI doesn't contain README file!
  preBuild = ''
    echo "Long description" > readme.md
  '';

  propagatedBuildInputs = [
    nose
    twine
    colorama
  ];

  # No check avaliable
  doCheck = false;
}
