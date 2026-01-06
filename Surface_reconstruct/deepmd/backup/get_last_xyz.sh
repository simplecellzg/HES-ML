  Natom=$(head -n 1 $1)
  echo $Natom
  nl=$((Natom+2))
  fn=$(echo $1)
  tail -n $nl $1 > ${fn}-last-frame.xyz