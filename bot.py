import os
import logging
import time

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Import environment variables
from dotenv import load_dotenv

load_dotenv()

DELAY_BETWEEN_URL_CHECKS = int(os.getenv("DELAY_BETWEEN_URL_CHECKS", "5"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__file__)


def check_availability(url: str):

    # Get the event by getting the last string after a "/" from the url
    event = url.split("/")[-1]

    log.info(f"Checking availability for event #{event}")

    # ------------------------------ Webdriver setup ----------------------------- #
    try:
        log.info("Starting driver...")
        options = webdriver.FirefoxOptions()

        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Remote(
            command_executor="http://browser:4444/wd/hub", options=options
        )

        # Changing the property of the navigator value for webdriver to undefined
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    except Exception as e:
        return exit(f"The driver could not be started: {e}", None, None)

    # ------------------------------- Open website ------------------------------- #
    try:
        log.info(f"Navigating to Ticketmaster...")
        driver.get(url)
        # Wait until page loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main-content"))
        )
        time.sleep(2)
    except:
        return exit("Could not open the Ticketmaster site", None, driver)

    # -------------------- Check if there is any availability -------------------- #
    # Check if there is a span class with the text "Sorry, we couldn't find any results"
    try:
        log.info("Checking availability...")
        driver.find_element(By.CLASS_NAME, "tm-availability__message")
        log.info("No availability found.")
        return exit(None, False, driver)
    except:
        log.info("Availability found!")
        return exit(None, True, driver)


def exit(error, availability, driver):
    if error:
        log.error(error)

    if driver is not None:
        try:
            # CLose driver
            log.info("Closing driver...")
            driver.close()
            driver.quit()
        except:
            pass

    return [error, availability]


if __name__ == "__main__":
    url_list = os.getenv("URL_LIST", "").split(",")

    for url in url_list:
        check_availability(url)
        time.sleep(DELAY_BETWEEN_URL_CHECKS)
