#!/bin/bash

#USAGE:
# lmp_atom2charge.sh <file1.lmp> <file2.lmp> ...

#DESCRIPTION:
# This script keeps the first two columns
# of data, adds "0.0" as a third column, and
# copies the remaining columns of data,
# to one or many files. It is intended
# for changing a LAMMPS data file from
# the atom_style "atomic" into "charge".

if [[ -z "$@" ]]; then
  printf "Add a column containing zeros to LAMMPS data files (*.lmp) to comply to 'atom_style charge'. \n"
  printf "Usage: lmp_atom2charge.sh <file1.lmp> [<file2.lmp> ...] \n"
else
  FILES="$@"
  for f in $FILES
  do
    printf ">>> Converting $f for 'atom_style charge'..."
    if [ -e $f ]; then
      #Check that it is a LAMMPS file
      islmp=$(grep "atom types" $f | wc -l)
      if [ $islmp = 1 ]; then
        # If the keyword "Atoms" is not followed by "# charge", add it
        atomic=$(grep "Atoms" $f | grep "charge" | wc -l)
        if [ $atomic = 0 ]; then
          sed -i '/Atoms/ c\Atoms  # charge' $f
        fi
        # Add a column of zero after column 2, keeping all other columns
        awk 'BEGIN {atoms_section=0}
             /^Atoms/ {atoms_section=1; print; next}
             /^$/ {if(atoms_section==1) atoms_section=2; print; next}
             {
               if(atoms_section==2 && NF>=5) {
                 # This is an atom line: ID type x y z [vx vy vz]
                 printf "%s\t%s\t0.0", $1, $2
                 for(i=3; i<=NF; i++) printf "\t%s", $i
                 printf "\n"
               } else {
                 print
               }
             }' $f >/tmp/temp.lmp
        mv -f /tmp/temp.lmp $f
        printf " Done.\n"
      else
        printf " Not a LAMMPS data file, skipping.\n"
      fi
    else
      printf " File doesn't exist, skipping.\n"
    fi
  done
fi
