import os
import time
import requests
import gzip
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def download_file(url, destination):
    """Download a file from a URL and save it to the destination."""
    response = requests.get(url)
    with open(destination, 'wb') as file:
        file.write(response.content)

def decompress_gz_to_tsv(gz_file, tsv_file):
    """Decompress a .gz file to a .tsv file and remove the .gz file after extraction."""
    with gzip.open(gz_file, 'rb') as f_in:
        with open(tsv_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"Decompressed {gz_file} to {tsv_file}")
    os.remove(gz_file)  # Remove the .gz file
    print(f"Removed {gz_file}")

def scrape_tcga_data():
    base_url = "https://xenabrowser.net/datapages/?hub=https://tcga.xenahubs.net:443"
    
    # Create the 'cohorts' directory if it doesn't exist
    output_dir = "cohorts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    driver = setup_driver()
    
    try:
        print(f"Navigating to {base_url}")
        driver.get(base_url)
        
        # Wait for the page to load
        time.sleep(10)
        
        print("Attempting to find cohort links...")
        cohort_links = driver.find_elements(By.CSS_SELECTOR, "li.MuiTypography-root a")
        
        if not cohort_links:
            print("No cohort links found. Trying alternative selector...")
            cohort_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'cohort=TCGA')]")
        
        if not cohort_links:
            print("Still no cohort links found. Dumping page source for debugging.")
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise Exception("Unable to find cohort links. Page source has been saved for debugging.")

        print(f"Found {len(cohort_links)} cohort links")

        for cohort_link in cohort_links:
            cohort_name = cohort_link.text.split('(')[0].strip()
            cohort_url = cohort_link.get_attribute('href')
            print(f"Processing cohort: {cohort_name}")

            try:
                # Open cohort page in a new tab
                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(cohort_url)
                
                # Wait for the page to load
                time.sleep(5)

                # Find and click the "IlluminaHiSeq pancan normalized" link
                pancan_link = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "IlluminaHiSeq pancan normalized"))
                )
                pancan_link.click()

                # Find the download link
                download_link = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.gz']"))
                )
                download_url = download_link.get_attribute('href')

                # Set the file paths inside the 'cohorts' directory
                gz_file_name = os.path.join(output_dir, f"{cohort_name.replace(' ', '_')}_HiSeqV2_PANCAN.gz")
                tsv_file_name = gz_file_name.replace(".gz", ".tsv")

                # Download the file
                download_file(download_url, gz_file_name)
                print(f"Downloaded: {gz_file_name}")

                # Decompress the .gz file to a .tsv file
                decompress_gz_to_tsv(gz_file_name, tsv_file_name)

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error occurred while processing {cohort_name}: {str(e)}")
            finally:
                # Close the tab and switch back to the main window
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    except WebDriverException as e:
        print(f"WebDriver exception occurred: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_tcga_data()