import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

def init_driver():
    options = uc.ChromeOptions()
    options.headless = True  # Run in headless mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors")
    
    driver = uc.Chrome(options=options)
    return driver

def scrape_page(driver, writer):
    businesses = driver.find_elements(By.CSS_SELECTOR, 'div.paper_paper__1PY90')
    for business in businesses:
        try:
            name = business.find_element(By.CSS_SELECTOR, 'p.typography_heading-xs__jSwUz').text
            rating = business.find_element(By.CSS_SELECTOR, 'div.star-rating_starRating__4rrcf img').get_attribute('alt').split()[1]
            review_count = business.find_element(By.CSS_SELECTOR, 'p.styles_ratingStats__lxP3v').text.split('|')[1].strip().split()[0].replace(',', '')
            review_count = int(review_count)
            business_url = business.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

            driver.get(business_url)
            time.sleep(2)

            phone = driver.find_element(By.CSS_SELECTOR, 'a[href^="tel:"]').text if driver.find_elements(By.CSS_SELECTOR, 'a[href^="tel:"]') else 'N/A'
            email = driver.find_element(By.CSS_SELECTOR, 'a[href^="mailto:"]').get_attribute('href').replace('mailto:', '').strip() if driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]') else 'N/A'
            website = driver.find_element(By.CSS_SELECTOR, 'a[href^="http"]').get_attribute('href') if driver.find_elements(By.CSS_SELECTOR, 'a[href^="http"]') else 'N/A'

            writer.writerow([name, rating, review_count, phone, email, website])
            print(f"Saved business: {name}, Rating: {rating}, Reviews: {review_count}, Phone: {phone}, Email: {email}, Website: {website}")
        except Exception as e:
            print(f"Error processing business: {e}")

def main():
    url = 'https://uk.trustpilot.com/categories/insurance'
    driver = init_driver()

    with open('insurance_agencies.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Business Name', 'Rating', 'Review Count', 'Phone Number', 'Email', 'Website'])

        page_num = 1
        driver.get(url)
        while True:
            try:
                print(f"Scraping page {page_num}")
                scrape_page(driver, writer)
                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[name="pagination-button-next"]')))
                next_button.click()
                time.sleep(2)
                page_num += 1
            except Exception as e:
                print(f"No more pages to load or error: {e}")
                break

    driver.quit()

if __name__ == "__main__":
    main()
