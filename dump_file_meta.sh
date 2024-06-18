#!/usr/bin/bash -e

find obj.vassalengine.org/images/[0-9a-f] -type f -printf '%p\0' | while IFS= read -r -d '' m ; do
  echo -ne "https://$m\t"
  stat --printf '%s\t' "$m"
  sha256sum "$m" | cut -f1 -d' ' | tr '\n' '\t'
  if [[ $m == *.vmod || $m == *.vext ]] ; then
    ( unzip -p "$m" moduledata | grep -Po '(?<=<version>).*(?=</version>)' ) || echo
  else
    echo
  fi
done
