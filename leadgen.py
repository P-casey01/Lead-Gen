import requests
from bs4 import BeautifulSoup
import csv
import time

# Base URL template for Trustpilot Insurance Agencies
url_template = 'https://uk.trustpilot.com/categories/insurance_agency?page={}'

# Initialize CSV
with open('insurance_agencies.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Business Name', 'Phone Number', 'Email', 'Website', 'Review Count', 'Average Rating'])

    # Iterate through pages 21 to 30
    for page in range(30, 20, -1):
        url = url_template.format(page)
        print(f"Scraping page {page} with URL: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # More accurate selector based on the provided HTML structure
            businesses = soup.select('section[data-service-review-card-list] > div')
            print(f"Found {len(businesses)} businesses on page {page}")

            for i, business in enumerate(businesses, start=1):
                print(f"Processing business {i} on page {page}")
                try:
                    name = business.select_one('p.typography_heading-xs__jSwUz').text.strip() if business.select_one('p.typography_heading-xs__jSwUz') else 'N/A'
                    rating_element = business.select_one('div.star-rating_starRating__4rrcf > img')
                    review_count_element = business.select_one('p.typography_body-m__xgxZ_')
                    website_element = business.select_one('a.typography_body-s__5nSN0')
                    
                    rating = float(rating_element['alt'].split()[0]) if rating_element else None
                    reviews = int(review_count_element.text.strip().split()[0]) if review_count_element else None
                    website = website_element['href'].strip() if website_element else ''
                    phone = 'N/A'  # Placeholder for phone
                    email = 'N/A'  # Placeholder for email
                    
                    # Apply filter
                    if (rating and rating < 4) or (reviews and reviews < 10):
                        if name and phone != 'N/A' and email != 'N/A' and website:
                            writer.writerow([name, phone, email, website, reviews, rating])
                            print(f"Saved business: {name}")
                        else:
                            print(f"Skipping business {name} due to missing phone, email, or website")
                    else:
                        print(f"Skipping business {name} due to high rating or review count")

                except Exception as e:
                    print(f"Error processing business {i} on page {page}: {e}")
        else:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")

        # Respect rate limits
        time.sleep(5)  # Adjust the sleep time as needed to avoid detection

print("Data extraction complete and saved to 'insurance_agencies.csv'")
