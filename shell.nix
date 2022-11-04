with (import <nixpkgs> {});

pkgs.mkShell {
 buildInputs = with pkgs; [
    python3Packages.mkdocs
    python3Packages.mkdocs-material
  ];
}


