{ pkgs ? import <nixpkgs> {}
}:

pkgs.mkShell {
  buildInputs = with pkgs.python3Packages; [
    mkdocs
    mkdocs-material
    mkdocs-git-revision-date-localized-plugin
  ];
}


