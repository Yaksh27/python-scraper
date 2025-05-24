import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OdishaRERAScraper:
    def __init__(self, headless=True):
        opts = Options()
        if headless:
            opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=opts)
        self.wait = WebDriverWait(self.driver, 15)
        self.list_url = "https://rera.odisha.gov.in/projects/project-list"

    def _safe_click(self, el):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.3)
        try:
            el.click()
        except ElementClickInterceptedException:
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", el)

    def _load_list(self):
        self.driver.get(self.list_url)
        time.sleep(1.5)
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Accept') or contains(.,'OK')]"))
            )
            self._safe_click(btn)
        except TimeoutException:
            pass
        self.wait.until(EC.presence_of_element_located((
            By.XPATH, "//a[contains(@class,'btn-primary') and normalize-space(.)='View Details']"
        )))

    def _wait_for_loader(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((
                By.CSS_SELECTOR, "ngx-ui-loader"
            )))
        except:
            pass

    def _safe_find(self, locator, timeout=7):
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            txt = el.text.strip()
            return txt if txt else "--"
        except TimeoutException:
            return "--"

    def _safe_find_multiple(self, locators, timeout=8):
        for locator in locators:
            txt = self._safe_find(locator, timeout)
            if txt and txt != "--":
                return txt
        return "--"

    def scrape(self):
        rows = []
        for idx in range(6):
            print(f"\n--- Processing project {idx+1} ---")
            self._load_list()
            buttons = self.driver.find_elements(By.XPATH, "//a[contains(@class,'btn-primary') and normalize-space(.)='View Details']")
            if idx >= len(buttons):
                rows.append({k: "--" for k in ("project_name","rera_regd_no","promoter_name","promoter_address","gst_no")})
                continue

            print("Clicking View Details…")
            self._safe_click(buttons[idx])
            self._wait_for_loader()
            time.sleep(1.5)

            # Project Name
            project_name = self._safe_find_multiple([
                (By.XPATH, "//label[contains(text(),'Project Name')]/following-sibling::strong"),
                (By.XPATH, "//div[contains(@class,'details-project ms-3')]//strong"),
                (By.XPATH, "//div[contains(@class,'details-project')][.//label[contains(text(),'Project Name')]]/strong"),
            ], timeout=10)
            print(f"  Project Name: {project_name}")

            # RERA Regd No
            rera_no = self._safe_find_multiple([
                (By.XPATH, "//label[contains(text(),'RERA Regd')]/following-sibling::strong"),
                (By.XPATH, "//label[contains(text(),'RERA Regd')]/following-sibling::*"),
                (By.XPATH, "//div[contains(@class,'details-project ms-3')][.//label[contains(text(),'RERA Regd')]]/strong"),
            ], timeout=10)
            print(f"  RERA Regd. No: {rera_no}")

            # Promoter Tab
            try:
                tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space(.)='Promoter Details']")))
                print("Switching to Promoter Details…")
                self._safe_click(tab)
                self._wait_for_loader()
                time.sleep(1.2)
            except TimeoutException:
                print("Promoter tab missing; trying fallback locators.")
                promoter_name = promoter_address = gst_no = "--"
            else:
               # Promoter Name: Tries both "Company Name" and "Proprietor Name"
                promoter_name = self._safe_find_multiple([
                    (By.XPATH, "//label[contains(text(),'Company Name')]/following-sibling::strong"),
                    (By.XPATH, "//label[contains(text(),'Company Name')]/following-sibling::*"),
                    (By.XPATH, "//label[contains(text(),'Propietory Name')]/following-sibling::strong"),
                    (By.XPATH, "//label[contains(text(),'Propietory Name')]/following-sibling::*"),
                ])

                # Promoter Address: Tries both "Registered Office Address" and "Permanent Address"
                promoter_address = self._safe_find_multiple([
                    (By.XPATH, "//label[contains(text(),'Registered Office Address')]/following-sibling::strong"),
                    (By.XPATH, "//label[contains(text(),'Registered Office Address')]/following-sibling::*"),
                    (By.XPATH, "//label[contains(text(),'Permanent Address')]/following-sibling::strong"),
                    (By.XPATH, "//label[contains(text(),'Permanent Address')]/following-sibling::*"),
                ])

                gst_no = self._safe_find_multiple([
                    (By.XPATH, "//label[contains(text(),'GST No')]/following-sibling::strong"),
                    (By.XPATH, "//label[contains(text(),'GST No')]/following-sibling::*"),
                ])
                print(f"  Promoter Name: {promoter_name}")
                print(f"  Promoter Address: {promoter_address}")
                print(f"  GST No: {gst_no}")

            rows.append({
                "project_name": project_name,
                "rera_regd_no": rera_no,
                "promoter_name": promoter_name,
                "promoter_address": promoter_address,
                "gst_no": gst_no
            })

        return pd.DataFrame(rows)

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = OdishaRERAScraper(headless=True)  # change it to false if you want to see the clicks...
    df = scraper.scrape()
    scraper.close()
    print("\nDone - here are your results:\n")
    print(df.to_csv(index=False))
    df.to_csv("odisha_rera_projects.csv", index=False)
