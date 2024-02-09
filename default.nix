{ pkgs ? import <nixpkgs> {}
}:

pkgs.stdenv.mkDerivation {
  name = "denog-routing-guide";

  src = ./.;

  buildInputs = with pkgs.python3Packages; [
    mkdocs
    mkdocs-material
    mkdocs-git-revision-date-localized-plugin
  ];

  buildPhase = ''
    mkdocs build -d $out
  '';
}


