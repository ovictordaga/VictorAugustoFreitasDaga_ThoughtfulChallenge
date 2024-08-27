from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from robocorp import workitems
import time
import re
import os
import re

class PayloadManager:
    def __init__(self, payload_data):
        self.payload_data = payload_data

    def get_search_phrase(self, index=0):
        return self.payload_data[index]["search_phrase"]

    def get_news_category(self, index=0):
        return self.payload_data[index]["news_category_section_topic"]

    def get_period(self, index=0):
        return self.payload_data[index]["period"]

class NewsScraper:
    def __init__(self, page, search_phrase):
        self.page = page
        self.search_phrase = search_phrase.lower()

    def get_news_items(self):
        """Extract all news items from the page."""
        news_items = []
        articles = self.page.query_selector_all("li > ps-promo")  # Select all promo elements inside <li> tags
        
        for article in articles:
            title = self.get_title(article)
            date = self.get_date(article)
            description = self.get_description(article)
            picture_filename = self.download_image(article, title)
            phrase_count = self.count_search_phrases(title, description)
            contains_money = self.contains_money(title, description)
            
            news_items.append({
                "title": title,
                "date": date,
                "description": description,
                "picture_filename": picture_filename,
                "phrase_count": phrase_count,
                "contains_money": contains_money
            })
        
        return news_items

    def get_title(self, article):
        """Extract the title of the news article."""
        title_element = article.query_selector("h3.promo-title > a")
        return title_element.inner_text().strip() if title_element else "No Title Found"

    def get_date(self, article):
        """Extract the date of the news article."""
        date_element = article.query_selector("p.promo-timestamp")
        return date_element.inner_text().strip() if date_element else "No Date Found"

    def get_description(self, article):
        """Extract the description of the news article."""
        description_element = article.query_selector("p.promo-description")
        return description_element.inner_text().strip() if description_element else "No Description Found"

    def sanitize_filename(self, title):
        """Sanitize the title to create a valid filename."""
        filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)  # Replace invalid characters with underscores
        return filename[:50]  # Truncate to avoid overly long filenames

    def download_image(self, article, title):
        """Download the image associated with the news article."""
        image_element = article.query_selector("img")
        if image_element:
            image_url = image_element.get_attribute("src")
            image_filename = self.sanitize_filename(title) + os.path.splitext(image_url)[-1]
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
        return bool(re.search(money_regex, title)) or (description and re.search(money_regex, description))

def save_to_excel(news_items):
    """Save the news items to an Excel file."""
    excel = Files()
    excel.create_workbook("output/news_data.xlsx")
    
    # Create a worksheet
    excel.create_worksheet("News Data")
    
    # Define the headers
    headers = ["Title", "Date", "Description", "Picture Filename", "Count of Search Phrases", "Contains Money"]
    excel.append_rows_to_worksheet([headers], "News Data")
    
    # Append the news items as rows
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
    
    # Save the workbook
    excel.save_workbook()


@task
def thoughtful_maestro_python():
    """Main task to scrape news data and save it to Excel."""
    browser.configure(slowmo=100)
    payload_manager = PayloadManager(receive_payload())
    
    open_the_news_website()
    input_search_phrase(payload_manager.get_search_phrase())
    apply_filters(payload_manager.get_news_category())
    time.sleep(10)

    # Scrape news items
    news_items = scrape_news(payload_manager.get_search_phrase())

    # Save the scraped news items to an Excel file
    save_to_excel(news_items)

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
        page.goto("https://www.latimes.com/", wait_until="load")
        page.wait_for_selector("xpath=//button[@data-element='search-button']", timeout=10000)
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
            page.check(checkbox_xpath)
            print(f"Category '{category}' selected successfully.")
        else:
            print("No category specified, only 'Newest' option selected.")
    
    except Exception as e:
        print(f"Error: The category '{category}' could not be found or selected. Exception: {e}")

def scrape_news(search_phrase):
    """Scrape news data from the page."""
    page = browser.page()
    scraper = NewsScraper(page, search_phrase)
    return scraper.get_news_items()



def log_in():
    """Fills in the login form and clicks the 'Log in' button"""
    page = browser.page()
    page.fill("#username", "maria")
    page.fill("#password", "thoushallnotpass")
    page.click("button:text('Log in')")

def fill_and_submit_sales_form(sales_rep):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()
    page.fill("#firstname", sales_rep["First Name"])
    page.fill("#lastname", sales_rep["Last Name"])
    page.select_option("#salestarget", str(sales_rep["Sales Target"]))
    page.fill("#salesresult", str(sales_rep["Sales"]))
    page.click("text=Submit")

def fill_form_with_excel_data():
    """Read data from excel and fill in the sales form"""
    excel = Files()
    excel.open_workbook("SalesData.xlsx")
    worksheet = excel.read_worksheet_as_table("data", header=True)
    excel.close_workbook()
    for row in worksheet:
        fill_and_submit_sales_form(row)

def download_excel_file():
    """Downloads excel file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/SalesData.xlsx", overwrite=True)

def collect_results():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="output/sales_summary.png")

def log_out():
    """Presses the 'Log out' button"""
    page = browser.page()  
    page.click("text=Log out")

def export_as_pdf():
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#sales-results").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, "output/sales_results.pdf")
