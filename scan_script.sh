#!/bin/bash
TIMESTAMP=$(date +%y%m%d)
echo "Scripts started"


# Function to convert PDF to simple text
convert_to_text() {
    echo start converting to txt
    pdftotext "$1" "$2"
}


# Function to convert PDF to scanned text using OCR
convert_to_scanned_text() {
#    tesseract "$1" "$2" -l ukr eng
    echo Start converting to scans to txt
    ./convertRecognizeScan.sh "$1" "$2" $count
}

# Function to convert DOC, DOCX, XLS, XLSX to simple text using LibreOffice
convert_to_text_with_libreoffice() {
    libreoffice --convert-to txt:Text --outdir "$2" "$1"
    echo "$1" "$2" converted to doc_scan
}

# Function to search for keywords in a text file
search_keywords() {
    full_path="$1"
    last_part=$(basename "$full_path")
    var=$(grep -iEo 'Dahua|Hikvision|Tiandy|Дахуа|Хіквіжн|Тіанді' "$full_path") && echo "Keyword: $var" | tee -a $input_directory/output.log && echo "Match found: $last_part" | tee -a $input_directory/output.log
#    grep -iE 'Метобезпека|Hikvision|Tiandy|Дахуа|Токар|Тіанді' "$1" && echo "Match found in $1"
#    grep -iE 'Dahua|Hikvision|Tiandy|Дахуа|Хіквіжні|Тіанді' "$1" && echo "Match found in $1"
}

# Directory containing PDF and document files
input_directory="$1"

# Output directory for text files
output_directory="${input_directory}/${TIMESTAMP}_txt_files"

# Ensure the output directory exists
if mkdir "$output_directory"
  then
  echo "$output_directory was created"
fi

#Remove all unnecessary files
if ls "${input_directory}"/*.p7s || ls "${input_directory}"/*yaml
  then
  rm "${input_directory}"/*.p7s "${input_directory}"/*.yaml
  echo "Junked files removed"
fi

# Loop through each file in the directory
count=0
for file_path in "$input_directory"/*; do
    echo "Working with $file_path and count #$count"
    if [ -f "$file_path" ]; then
        # Generate file names for text conversion
        base_name=$(basename "$file_path")
        base_name_no_ext="${base_name%.*}"
        text_file="$output_directory/${base_name_no_ext}.txt"
        text_file_scan="$output_directory/${base_name_no_ext}_scan.txt"

        # Convert PDF to simple text
        if [[ "$file_path" == *.pdf ]] || [[ $(file -b --mime-type "$file_path") == "application/pdf" ]]; then
            convert_to_text "$file_path" "$text_file"

            # Get the size of the file in bytes
            file_size=$(stat -c %s "$text_file")

            # Check if the file size is less than 20 bytes
            if [ $file_size -lt 50 ]
            then
              echo "Pdftext failed. The size of the file $file_size It is scanned doc."
              convert_to_scanned_text "$file_path" "$text_file_scan" $count

            fi
        fi

        # Convert DOC, DOCX, XLS, XLSX to simple text using LibreOffice
        if [[ "$file_path" == *.doc || "$file_path" == *.docx || "$file_path" == *.xls || "$file_path" == *.xlsx ]]; then
            convert_to_text_with_libreoffice "$file_path" "$output_directory"
        fi

        # Search for keywords in the text file
        search_keywords "$text_file"
        search_keywords "$text_file_scan"

        echo "========================================="
    fi
  count=$[$count+1]
done