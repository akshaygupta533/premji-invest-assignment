import re
import time
from urllib.parse import quote

from src.logger import make_logger
from src.api import get_senti_score
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from selenium import webdriver
from selenium.webdriver.common.by import By

# SELENIUM_SERVER_URL = os.environ["SELENIUM_SERVER_URL"]
SELENIUM_SERVER_URL = "http://host.docker.internal:4444/wd/hub"
DUMMY_API_URL = "http://host.docker.internal:80"
YOURSTORY_SEARCH_URL = "https://yourstory.com/search?q=KEYWORD&page=1"
FINSHOTS_URL = "https://finshots.in"

log = make_logger("pipeline")


class WebScraper:
    def __init__(self, retries=5):
        # URL of the remote WebDriver server

        selenium_server_url = SELENIUM_SERVER_URL

        options = webdriver.FirefoxOptions()

        for _ in range(retries):
            try:
                self.driver = webdriver.Remote(
                    command_executor=selenium_server_url, options=options
                )
                break
            except Exception as e:
                log.error("Could not connect to selenium server")
                log.error(e)
                log.error("Retrying....")
                time.sleep(2)
        self.driver.implicitly_wait(5)

    def reinit_driver(self):
        self.driver.quit()
        selenium_server_url = SELENIUM_SERVER_URL

        options = webdriver.FirefoxOptions()

        self.driver = webdriver.Remote(
            command_executor=selenium_server_url, options=options
        )
        self.driver.implicitly_wait(5)

    def clean_text(self, text):
        text = re.sub(r"[^a-zA-Z\s]", "", text)  # Clean special characters
        text = text.lower()  # Convert to lowercase
        tokens = text.split()  # Tokenize text
        stop_words = set(stopwords.words("english"))
        filtered_tokens = [token for token in tokens if token not in stop_words]
        lemmatizer = WordNetLemmatizer()
        lemmtized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
        clean_text = " ".join(lemmtized_tokens)
        return clean_text

    def get_yourstory_top_5(self, keyword):
        url = YOURSTORY_SEARCH_URL.replace("KEYWORD", quote(keyword))

        self.driver.get(url)
        elements = self.driver.find_elements(
            By.XPATH, "//div//li//span[@pathname='/search']"
        )[:5]
        links = [
            el.find_element(By.XPATH, "./ancestor::a").get_attribute("href")
            for el in elements
        ]
        return links

    def get_yourstory_article_sentiment_score(self, url):
        # re-init the webdriver to prevent blocking from website
        self.reinit_driver()
        self.driver.get(url)
        article_div = self.driver.find_element(
            By.XPATH, "//div[@id='article_container']"
        )
        article_text = article_div.text
        cleaned_text = self.clean_text(article_text)
        score = get_senti_score(cleaned_text)
        return score

    def get_finshots_article_sentiment_score(self, url):
        self.driver.get(url)
        article_div = self.driver.find_element(By.XPATH, "//div[@class='post-content']")
        article_text = article_div.text
        cleaned_text = self.clean_text(article_text)
        score = get_senti_score(cleaned_text)
        return score

    def get_finshots_top_5(self, keyword):
        url = FINSHOTS_URL
        self.driver.get(url)
        search_class_name = "toggle-search-button"
        search_button = self.driver.find_element(
            By.CSS_SELECTOR, f"a.{search_class_name}"
        )
        search_button.click()
        input_field = self.driver.find_element(By.XPATH, "//input[@type='search']")
        input_field.send_keys(keyword)
        article_elements = self.driver.find_elements(
            By.XPATH, "//a[@class='c-search-result']"
        )[:5]
        links = [el.get_attribute("href") for el in article_elements]
        return links

    def close_driver(self):
        self.driver.quit()
