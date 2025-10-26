{ pkgs }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.chromium
    pkgs.chromedriver
    pkgs.pkg-config
    pkgs.cairo
    pkgs.glib
    pkgs.gdk-pixbuf
    pkgs.gtk3
    pkgs.at-spi2-atk
    pkgs.xorg.libX11
    pkgs.xorg.libXcomposite
    pkgs.xorg.libXcursor
    pkgs.xorg.libXdamage
    pkgs.xorg.libXext
    pkgs.xorg.libXfixes
    pkgs.xorg.libXi
    pkgs.xorg.libXrandr
    pkgs.xorg.libXrender
    pkgs.xorg.libXScrnSaver
    pkgs.xorg.libXtst
    pkgs.xorg.libxcb
    pkgs.nss
    pkgs.freetype
    pkgs.fontconfig
    pkgs.pango
    pkgs.harfbuzz
    pkgs.sqlite
    pkgs.libdrm
    pkgs.libxshmfence
    pkgs.xdg-utils
    pkgs.dbus
  ];
  shellHook = ''
    export CHROME_BIN=chromium
    export CHROMEDRIVER_BIN=chromedriver
  '';
}
