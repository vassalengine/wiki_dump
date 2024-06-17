#!/usr/bin/bash -e

find obj.vassalengine.org/images/[0-9a-f] -type f \( -name '*.vmod' -o -name '*.mod' \) -printf '%p\0' | while IFS= read -r -d '' m ; do
  echo -ne "https://$m\t"
  stat --printf '%s\t' "$m"
  sha256sum "$m" | cut -f1 -d' ' | tr '\n' '\t'
  ( unzip -p "$m" moduledata | grep -Po '(?<=<version>).*(?=</version>)' ) || echo
done
