from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from robocorp import workitems
import time

class PayloadManager:
    def __init__(self, payload_data):
        self.payload_data = payload_data

    def get_search_phrase(self, index=0):
        return self.payload_data[index]["search_phrase"]

    def get_news_category(self, index=0):
        return self.payload_data[index]["news_category_section_topic"]

    def get_period(self, index=0):
        return self.payload_data[index]["period"]

@task
def thoughtful_maestro_python():
    """Insert the sales data for the week and export it as a PDF"""
    browser.configure(slowmo=100)
    payload_manager = PayloadManager(receive_payload())
    
    open_the_news_website()
    input_search_phrase(payload_manager.get_search_phrase())
    time.sleep(10)
    # Additional tasks using payload_manager...

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
        page.goto("https://www.latimes.com/", timeout=60000)
        # Instead of waiting for the full page load, just wait for the specific element
        page.wait_for_selector("xpath=//button[@data-element='search-button']", timeout=10000)
        print("Search button is loaded.")
    except Exception as e:
        print(f"Failed to load the page or find the element: {e}")

def input_search_phrase(search_phrase):
    """Searches for the given phrase"""
    page = browser.page()
    page.click("xpath=//button[@data-element='search-button']")
    page.fill("xpath=//input[@data-element='search-form-input']", search_phrase)

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
