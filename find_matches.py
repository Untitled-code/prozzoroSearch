import subprocess


def check_files(pdf_folder_path):
    bash_script_path = './scan_script.sh'
    match_keyword_list = []
    match_filename_list = []

    print(f"Start with {bash_script_path} and {pdf_folder_path}")
    # Run the Bash script with the PDF folder as an argument
    result = subprocess.run([bash_script_path, pdf_folder_path], capture_output=True, text=True)

    # Get the output and split it into lines
    output_lines = result.stdout.splitlines()

    # Process each line to extract relevant information
    for line in output_lines:
        if "Keyword" in line:
            full_string = line.split(":", 1)
            match_keyword = full_string[1]
            print(f"Keyword found: {match_keyword}")
            match_keyword_list.append(match_keyword)
        if "Match found" in line:
            full_string_filename = line.split(":", 1)
            match_filename = full_string_filename[1]
            match_filename_list.append(match_filename)
            print(f"In the document: {match_filename}")

    # removing duplicates
    if match_keyword_list:
        match_keyword_set = set(match_keyword_list)
        print(match_keyword_set)
    else:
        match_keyword_set = 'none'

    if match_filename_list:
        match_filename_set = set(match_filename_list)
        print(match_filename_set)
    else:
        match_filename_set = 'none'

    return match_keyword_set, match_filename_set
