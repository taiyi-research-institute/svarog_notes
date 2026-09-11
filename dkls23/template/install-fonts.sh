#!/bin/sh
set -eu

google_fonts_rev=5e35378e6bda803962ee6fd257e444a7d459660d
font_src=$(mktemp -d)
texmf_local=$(kpsewhich -var-value=TEXMFLOCAL)
font_dst="$texmf_local/fonts/truetype/google/noto"
trap 'rm -rf "$font_src"' EXIT HUP INT TERM

command -v curl >/dev/null
command -v uvx >/dev/null
command -v mktexlsr >/dev/null
mkdir -p "$font_dst"

curl -fL "https://raw.githubusercontent.com/google/fonts/$google_fonts_rev/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf" -o "$font_src/NotoSerifSC-VF.ttf"
curl -fL "https://raw.githubusercontent.com/google/fonts/$google_fonts_rev/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf" -o "$font_src/NotoSansSC-VF.ttf"

printf '%s  %s\n' \
  050080d9255a86808f2945bffac582b31ef32bc36411ce29563b4961670c66f9 "$font_src/NotoSerifSC-VF.ttf" \
  a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da "$font_src/NotoSansSC-VF.ttf" \
  | sha256sum -c -

uvx --from fonttools==4.64.0 fonttools varLib.instancer "$font_src/NotoSerifSC-VF.ttf" wght=400 --output="$font_dst/NotoSerifSC-Regular.ttf"
uvx --from fonttools==4.64.0 fonttools varLib.instancer "$font_src/NotoSerifSC-VF.ttf" wght=700 --output="$font_dst/NotoSerifSC-Bold.ttf"
uvx --from fonttools==4.64.0 fonttools varLib.instancer "$font_src/NotoSansSC-VF.ttf" wght=400 --output="$font_dst/NotoSansSC-Regular.ttf"
uvx --from fonttools==4.64.0 fonttools varLib.instancer "$font_src/NotoSansSC-VF.ttf" wght=500 --output="$font_dst/NotoSansSC-Medium.ttf"
uvx --from fonttools==4.64.0 fonttools varLib.instancer "$font_src/NotoSansSC-VF.ttf" wght=700 --output="$font_dst/NotoSansSC-Bold.ttf"

mktexlsr "$texmf_local"
printf 'Installed DKLS23 fonts in %s\n' "$font_dst"
