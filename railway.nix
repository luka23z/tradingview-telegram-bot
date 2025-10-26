# force rebuild

{ pkgs }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.chromium
    pkgs.chromedriver
  ];
  shellHook = ''
    export CHROME_BIN=chromium
    export CHROMEDRIVER_BIN=chromedriver
  '';
}
