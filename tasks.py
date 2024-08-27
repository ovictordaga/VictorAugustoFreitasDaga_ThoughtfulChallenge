from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from robocorp import workitems
from datetime import datetime, timedelta
import time
import re
import os

class PayloadManager:
    def __init__(self, payload_data):
        self.payload_data = payload_data

    def get_search_phrase(self, index=0):
        if index < len(self.payload_data):
            return self.payload_data[index]["search_phrase"]
        else:
            raise IndexError("Index out of range for payload data.")

    def get_news_category(self, index=0):
        return self.payload_data[index]["news_category_section_topic"]

    def get_period(self, index=0):
        return self.payload_data[index]["period"]

class NewsScraper:
    def __init__(self, page, search_phrase, target_date):
        self.page = page
        self.search_phrase = search_phrase.lower()
        self.target_date = target_date

    def get_news_items(self):
        """Extract all news items from the page."""
        news_items = []
        articles = self.page.query_selector_all("li > ps-promo")  # Select all promo elements inside <li> tags
        
        should_continue = True  # Flag to determine whether to continue scraping
        
        for article in articles:
            title = self.get_title(article)
            date = self.get_date(article)
            if not date:
                continue  # Skip this article if the date is missing or invalid

            description = self.get_description(article)
            picture_filename = self.download_image(article, title)
            phrase_count = self.count_search_phrases(title, description)
            contains_money = self.contains_money(title, description)
            
            # Check if the article date is within the target range
            article_date = self.parse_date(date)
            if article_date and article_date < self.target_date:
                should_continue = False  # Set the flag to False, but continue processing other articles

            news_items.append({
                "title": title,
                "date": date,
                "description": description,
                "picture_filename": picture_filename,
                "phrase_count": phrase_count,
                "contains_money": contains_money
            })
        
        return news_items, should_continue  # Return all collected news items and the flag

    def get_title(self, article):
        """Extract the title of the news article."""
        title_element = article.query_selector("h3.promo-title > a")
        return title_element.inner_text().strip() if title_element else "No Title Found"

    def get_date(self, article):
        """Extract the date of the news article."""
        date_element = article.query_selector("p.promo-timestamp")
        return date_element.inner_text().strip() if date_element else None

    def parse_date(self, date_str):
        """Parse the date string to a datetime object."""
        # Month mapping dictionary
        month_map = {
            "Jan.": "January", "Jan": "January",
            "Feb.": "February", "Feb": "February",
            "Mar.": "March", "March": "March",
            "Apr.": "April", "April": "April",
            "Jun.": "June", "June": "June",
            "Jul.": "July", "July": "July",
            "Aug.": "August", "Aug": "August",
            "Sep.": "September", "Sep": "September",
            "Oct.": "October", "Oct": "October",
            "Nov.": "November", "Nov": "November",
            "Dec.": "December", "Dec": "December"
        }
        
        try:
            # Validate and replace the month abbreviation with the full month name
            valid_month = False
            for abbrev, full_month in month_map.items():
                if abbrev in date_str:
                    # Replace the abbreviation with the full month name
                    date_str = date_str.replace(abbrev, full_month)
                    valid_month = True
                    break
            
            # Check if the month was valid
            if not valid_month:
                raise ValueError(f"Invalid month abbreviation in date: {date_str}")

            # Parse the date with the full month name format, e.g., "August 26, 2024"
            return datetime.strptime(date_str, "%B %d, %Y")
        except ValueError as e:
            # Log the error if the date format is incorrect or contains typos
            print(f"Date format error: {date_str} - {e}")
            return None




    def get_description(self, article):
        """Extract the description of the news article."""
        description_element = article.query_selector("p.promo-description")
        return description_element.inner_text().strip() if description_element else "No Description Found"

    def sanitize_filename(self, title):
        """Sanitize the title to create a valid filename."""
        filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)  # Replace invalid characters with underscores
        return filename[:30]  # Truncate to avoid overly long filenames

    def download_image(self, article, title):
        """Download the image associated with the news article."""
        image_element = article.query_selector("img")
        if image_element:
            image_url = image_element.get_attribute("src")

            # Sanitize and verify the image filename
            image_filename = self.sanitize_filename(title)
            
            # Extract the extension from the URL or default to .jpg if not found
            ext = os.path.splitext(image_url)[-1]
            if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                ext = '.jpg'  # Default to .jpg if no valid extension is found

            # Truncate the filename to ensure it's within a safe length
            image_filename = image_filename[:50 - len(ext)]  # Adjust length to account for the extension

            # Add the extension to the truncated filename
            image_filename += ext

            # Download the image
            http = HTTP()
            http.download(image_url, f"output/{image_filename}")
            return image_filename
        return "No Image Found"

    def count_search_phrases(self, title, description):
        """Count the occurrences of the search phrase in title and description."""
        phrase_count = title.lower().count(self.search_phrase)
        if description:
            phrase_count += description.lower().count(self.search_phrase)
        return phrase_count

    def contains_money(self, title, description):
        """Check if the title or description contains any amount of money."""
        money_regex = r"(\$\d{1,3}(,\d{3})*(\.\d{2})?)|(\d+(\.\d{2})?\s*(USD|dollars?))"
        
        # Check if the title contains money
        if re.search(money_regex, title):
            return True
        
        # Check if the description contains money
        if description and re.search(money_regex, description):
            return True
        
        return False


def save_to_excel(news_items, append=False):
    """Save the news items to an Excel file."""
    excel = Files()
    
    if append and os.path.exists("output/news_data.xlsx"):
        excel.open_workbook("output/news_data.xlsx")
    else:
        excel.create_workbook("output/news_data.xlsx")
        excel.create_worksheet("News Data")
        headers = ["Title", "Date", "Description", "Picture Filename", "Count of Search Phrases", "Contains Money"]
        excel.append_rows_to_worksheet([headers], "News Data")
    
    for item in news_items:
        row = [
            item["title"],
            item["date"],
            item["description"],
            item["picture_filename"],
            item["phrase_count"],
            item["contains_money"]
        ]
        excel.append_rows_to_worksheet([row], "News Data")
    
    excel.save_workbook()

@task
def thoughtful_maestro_python():
    """Main task to scrape news data and save it to Excel."""
    browser.configure(slowmo=100)
    payload_manager = PayloadManager(receive_payload())
    
    open_the_news_website()
    input_search_phrase(payload_manager.get_search_phrase())
    apply_filters(payload_manager.get_news_category())
    time.sleep(5)

    period_months = payload_manager.get_period()
    target_date = datetime.now() - timedelta(days=period_months * 30)

    all_news_items = []
    page_number = 1
    first_page = True
    items_counter = 0  # Counter for tracking the number of items

    while True:
        print(f"Scraping page {page_number}...")

        news_items, should_continue = scrape_news(payload_manager.get_search_phrase(), target_date)

        if first_page and news_items:
            first_news_date = re.sub(r'\b(\w{3})\.\s', r'\1 ', news_items[0]['date'])
            first_news_datetime = datetime.strptime(first_news_date, "%b %d, %Y")
            if first_news_datetime < target_date:
                print("Warning: No news items found within the specified period.")
                return
        
        all_news_items.extend(news_items)
        items_counter += len(news_items)

        # Save items for every 10 items collected
        if items_counter >= 10:
            save_to_excel(all_news_items, append=True)
            all_news_items.clear()  # Clear the list after saving
            items_counter = 0  # Reset the counter after saving

        if not should_continue:
            break

        try:
            page = browser.page()
            next_button = page.query_selector("div.search-results-module-next-page a")
            if next_button:
                next_button.click()
                time.sleep(5)
                page.wait_for_load_state("load")
                page_number += 1
            else:
                print("No more pages found.")
                break
        except Exception as e:
            print(f"Failed to navigate to the next page: {e}")
            break
        
        first_page = False

    # Save any remaining items after finishing the loop
    if all_news_items:
        save_to_excel(all_news_items, append=True)


def receive_payload():
    collected_data = []
    for item in workitems.inputs:
        payload_data = {
            "search_phrase": item.payload["search phrase"],
            "news_category_section_topic": item.payload["news category/section/topic"],
            "period": item.payload["Period"]
        }
        collected_data.append(payload_data)
    return collected_data

def open_the_news_website():
    """Navigates to the given URL and waits for the search button to load"""
    try:
        page = browser.page()
        # Wait for the page to load with an increased timeout
        page.goto("https://www.latimes.com/", timeout=60000)
        
        # Wait for the search button to load with an increased timeout
        page.wait_for_selector("xpath=//button[@data-element='search-button']", timeout=20000)
        print("Search button is loaded.")
    except Exception as e:
        print(f"Failed to load the page or find the element: {e}")

def input_search_phrase(search_phrase):
    """Searches for the given phrase"""
    page = browser.page()
    page.click("xpath=//button[@data-element='search-button']")
    page.fill("xpath=//input[@data-element='search-form-input']", search_phrase)
    page.click("xpath=//button[@data-element='search-submit-button']")
    page.wait_for_load_state("load")

def apply_filters(category):
    """Apply filters for the search with error handling"""
    page = browser.page()
    
    try:
        page.select_option("select[name='s']", "1")  # Value "1" corresponds to "Newest"
        
        if category:
            checkbox_xpath = f"//span[text()='{category}']/preceding::input[@type='checkbox'][1]"
            page.wait_for_load_state("load")
            page.check(checkbox_xpath)
            time.sleep(10)
            page.wait_for_load_state("load")
            
            print(f"Category '{category}' selected successfully.")
        else:
            print("No category specified, only 'Newest' option selected.")
    
    except Exception as e:
        print(f"Error: The category '{category}' could not be found or selected. Exception: {e}")

def scrape_news(search_phrase, target_date):
    """Scrape news data from the page."""
    page = browser.page()
    scraper = NewsScraper(page, search_phrase, target_date)
    return scraper.get_news_items()
