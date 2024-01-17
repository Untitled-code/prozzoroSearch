from bs4 import BeautifulSoup

# Read HTML content from the text file
with open("bs.txt", "r", encoding="utf-8") as file:
    html = file.read()

# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all elements with the class 'search-result-card__description'
description_elements = soup.find_all(class_='search-result-card__description')

# Extract and print the ID values
id_values = []
for element in description_elements:
    id_text = element.find(string=lambda text: text and "ID:" in text)
    if id_text:
        id_values.append(id_text.replace("ID:", "").strip())
    else:
        print("N/A")

# Print the list of ID values
print(id_values)
