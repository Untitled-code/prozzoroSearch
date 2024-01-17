#!/bin/bash
# recognizing scans by tesseract and cleaning and converting to txt
output_file="$1"
echo "Output file for scans $output_file"

for file in $(ls *jpg | sort -t'-' -nk2.1) #sorting files by number
do
	echo "working with $file"
	filename="${file%%.*}"
	tesseract -l ukr+eng+rus "$file" "$filename" --psm 6 #tesseract scan every jpg file and convert to txt with columns
	sed 's/|//g' "$filename".txt | sed "s/['\"]//g" >> output.txt

done
cp ./output.txt ../../../"$output_file"
