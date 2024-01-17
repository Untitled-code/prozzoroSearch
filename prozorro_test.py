import json


# Corrected extract_document_urls function
def extract_document_urls(data, current_path="", document_urls=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            # print(f"if...{new_path}")
            if key == "documents":
                title = [doc.get("title") for doc in value]
                print(title)
                document_urls.append({"title": [doc.get("title") for doc in value],
                                      "urls": [doc.get("url") for doc in value]})
                # print(f"Documents urls... {document_urls}")
            extract_document_urls(value, new_path, document_urls)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{current_path}[{i}]"
            # print(f"Elif.. {new_path}")
            extract_document_urls(item, new_path, document_urls)


# Assuming 'your_json_data' is your loaded JSON data
# Replace this variable with your actual data
with open('./test_tender2.json', 'r') as file:
    your_json_data = json.load(file)

document_urls = []
# Call the function without passing 'urls' as a keyword argument
extract_document_urls(your_json_data, document_urls=document_urls)


# Print or use the extracted document URLs
for doc_urls in document_urls:
    print(f"Title: {doc_urls['title'][0]}, URLs: {doc_urls['urls'][0]}")
