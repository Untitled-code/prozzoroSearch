#!/bin/bash

file="$1"
output_file="$2"
count=$3
echo "Name of file: $file"
dir=$(dirname "$file")  # get dirname from path
newDir=${dir}/${count}_converted_scans
filename=$(basename "$file") #parse file from full path
mkdir -p "$newDir"
echo "New directory $(readlink -f "$newDir") is made"
cp "$file" "$newDir"/
if cd "$newDir"; then echo "Ok"; else echo "Fail"; fi # for custom handling
echo "cd to... $(pwd)"
echo "Making $newDir and copying target file $filename"
#
if ! convert-im6.q16 -density 300 ./"$filename" p.jpg
then
  echo "exit status $?. Bad file format"
else
  echo "starting tesseract with scanAndClean.sh"
  ../../../scanAndClean.sh "$output_file"

  # removing working directory
  working_dir=$(pwd)
  rm -r "$working_dir"
  echo "Done with $file"
fi