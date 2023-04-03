import requests
from bs4 import BeautifulSoup
import re
import csv
import os

# This is a regex to grab Australian phone numbers in a variety of formats.
australian_number_pattern = re.compile(r'''
    (?:\(\d\d\)\s\d{4}\s\d{4}| # (02) 1234 5678
    \d{2}\s\d{4}\s\d{4}| # 02 1234 5678
    \+\d{2}\s\d\s\d{4}\s\d{4}| # +61 2 1234 5678
    \+\d{2}\s\d{4}\s\d{4}| # +61 1234 5678
    \+\d{2}\s\d{4}\s\d{3}\s\d{3}| # +61 433 557 130
    \+\d{2}\s0\d{3}\s\d{3}\s\d{3}| # +61 0433 557 130
    \d{8}| # 12345678
    \d{4}\s\d{4}| # 1234 5678
    \d{4}-\d{4}| # 1234-5678
    \d{4}\.\d{4}| # 1234.5678
    \d{2}.?\d{4}.?\d{4}| # 02-1234-5678, 02.1234.5678
    (?:0|\+61\s?)?\d{3}?[\s.-]?\d{3}?[\s.-]?\d{3}?) # 0412 345 678, 0412-345-678, 0412.345.678, 0412345678, +61 412 345 678
     ''', re.VERBOSE)
    
# This is a regex to grab email addresses in a variety of formats.
email_pattern = re.compile(r'''
[\w.%+'-]+[\w._%+'-]*@[\w.-]+\.[a-zA-Z]{2,} # email address
''', re.VERBOSE)

# Compile regex patterns into regex objects
find_australian_numbers = re.compile(australian_number_pattern)
find_emails = re.compile(email_pattern)



def search_contact_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract visible text from the web page
    texts = soup.stripped_strings
    text = ' '.join(texts)

    # Find phone numbers and email addresses
    phone_numbers = set(find_australian_numbers.findall(text))
    emails = set(find_emails.findall(text))

    return phone_numbers, emails

# Fetch and parse the homepage
homepage_url = 'https://www.example.com'
response = requests.get(homepage_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Initialize the sets for phone numbers and email addresses
phone_numbers = set()
emails = set()

# Find and follow links that contain the keywords 'contact' or 'about'
keywords = ['contact', 'about']
for link in soup.find_all('a', href=True):
    if any(keyword.lower() in link['href'].lower() for keyword in keywords):
        target_url = link['href']

        # Check if the URL is relative and convert it to an absolute URL
        if not target_url.startswith('http'):
            target_url = requests.compat.urljoin(homepage_url, target_url)

        # Merge the sets of phone numbers and email addresses
        phone_numbers |= search_contact_details(target_url)[0]
        emails |= search_contact_details(target_url)[1]

        print(f"URL: {target_url}")
        print("Phone numbers:")
        for number in phone_numbers:
            print(number)

        print("\nEmail addresses:")
        for email in emails:
            print(email)
        print("\n")


print("Phone numbers found:") # will print the "phone numbers found" in the terminal
for number in phone_numbers:
    print(number)

print("Email addresses found:") # will print the "email addresses found" in the terminal
for email in emails:
    print(email)


# Save email addresses and their source to a CSV file
email_file = 'email_results.csv'
write_email_header = not os.path.exists(email_file)
with open('email_results.csv', mode='a', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Write header row if the file does not exist
    if write_email_header:
        csv_writer.writerow(['Email Address', 'Source'])

    # Write email addresses and their source
    for email in emails:
        csv_writer.writerow([email, target_url])

print("Email results have been saved to 'email_results.csv'.")

# Save phone numbers and their source to a CSV file
phone_file = 'phone_results.csv'
write_phone_header = not os.path.exists(phone_file)
with open('phone_results.csv', mode='a', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Write header row if the file does not exist
    if write_phone_header:
        csv_writer.writerow(['Phone Number', 'Source'])

    # Write phone numbers and their source
    for number in phone_numbers:
        csv_writer.writerow([number, target_url])

print("Phone results have been saved to 'phone_results.csv'.")