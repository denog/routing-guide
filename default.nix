{ pkgs ? import <nixpkgs> {}
}:

pkgs.stdenv.mkDerivation {
  name = "denog-routing-guide";

  src = ./.;

  buildInputs = with pkgs.python3Packages; [
    mkdocs
    mkdocs-material
  ];

  buildPhase = ''
    mkdocs build -d $out
  '';
}


