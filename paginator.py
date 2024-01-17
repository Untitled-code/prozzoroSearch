from bs4 import BeautifulSoup

# Read HTML content from the text file
with open("bs.txt", "r", encoding="utf-8") as file:
    html = file.read()

# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all buttons with the class 'paginate__btn'
page_buttons = soup.find_all(class_='paginate__btn')

# Extract page numbers and filter out non-numeric values
page_numbers = [int(button.text.strip()) for button in page_buttons if button.text.strip().isdigit()]

# Find the maximum page number
max_page_number = max(page_numbers) if page_numbers else 1

print(f"Number of pages: {max_page_number}")

