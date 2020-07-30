########################################################################
###### Collecting the news of "O Globo" related to the "Fake News" #####
########################################################################

########################################################################
# Importing the required libraries.
import re, csv, pandas as pd, numpy as np, time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
########################################################################

########################################################################
# 1. Defining the required functions
########################################################################

def init_webdriver(url, is_firefox=True):
    # Choosing the webdriver.
    if not is_firefox:
        # Running the PhantomJS webdriver.
        driver = webdriver.PhantomJS()
        driver.set_window_size(1120, 550)
    else:
        # Defining the option to the Firefox webdriver.
        options = Options()
        Options.set_headless = True

        # Running the Firefox webdriver.
        driver = webdriver.Firefox(
            executable_path = "/home/breno/geckodriver/geckodriver", options=options)

    # Getting the web page.
    driver.get(url)

    # Setting the time of page refresh to 1 day (24 hours).
    driver.execute_script("propriedadeTempoDoRefreshAutomatico = 86400000;")

    return driver


def authenticate(driver):
    # Waiting for 10 seconds.
    driver.implicitly_wait(10)

    # Clicking the button "ENTRAR".
    driver.find_element_by_id("barra-item-login").click()

    # Opening the iframe "login".
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it(
        (By.ID, "login-popin-iframe")))

    # Authenticating with user's account data.
    username_field = driver.find_element_by_id("login")
    password_field = driver.find_element_by_id("password")
    username_field.send_keys(">>> VALID USER/E-MAIL <<<")
    password_field.send_keys(">>> YOUR PASSWORD <<<")
    password_field.send_keys(Keys.RETURN)

    # Waiting for 10 seconds.
    driver.implicitly_wait(10)

    # Returning the main window.
    driver.switch_to.default_content()

    # Waiting for 10 seconds.
    driver.implicitly_wait(10)

    # Forcing the time of page refresh to be 1 day (24 hours).
    driver.execute_script("propriedadeTempoDoRefreshAutomatico = 86400000;")


def get_links(url):
    # Getting Firefox webdriver.
    driver = init_webdriver(url)

    # Clicking the button "PROSSEGUIR".
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.cookie-banner-lgpd_accept-button"))).click()

    # Clicking the button "CANCELAR".
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.ID, "onesignal-slidedown-cancel-button"))).click()

    while True:
        try:
            # Waiting to load the news.
            WebDriverWait(driver, 120).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".article-feed")))

            # Waiting to load the button "Ver Mais".
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                (By.CLASS_NAME, "article-feed__more-button")))

            # Scrolling down to the button and clicking it.
            button = driver.find_element_by_class_name("article-feed__more-button")
            driver.execute_script("arguments[0].scrollIntoView();", button)
            driver.execute_script("arguments[0].click();", button)
        except NoSuchElementException:
            break
        except TimeoutException:
            break
        except StaleElementReferenceException:
            break

    # Extracting the news URLs.
    html_soup = BeautifulSoup(driver.page_source, "html.parser")
    links = [link["href"] for link in html_soup.select("h1[class='article-feed-item__title'] > a")]

    # Closing the Firefox webdriver.
    driver.quit()

    return links


def get_data(url, links):
    # Getting PhantomJS webdriver.
    driver = init_webdriver(url, False)

    # Authenticating the valid user.
    authenticate(driver)

    data = []
    for idx, link in enumerate(links):
        try:
            # Getting the web page.
            driver.get(link)

            # Defining the scraper.
            html_soup = BeautifulSoup(driver.page_source, "html.parser")
            record = {}

            # Title.
            if html_soup.find("h1", class_="article__title"):
                record["title"] = re.sub(r"\s+", " ",
                    html_soup.find("h1", class_="article__title").string).strip()
            elif html_soup.select("div.head-materia > h1"):
                record["title"] = re.sub(r"\s+", " ",
                    html_soup.select("div.head-materia > h1")[0].string).strip()

            # Subtitle.
            if html_soup.find("div", class_="article__subtitle"):
                record["subtitle"] = re.sub(r"\s+", " ",
                    html_soup.find("div", class_="article__subtitle").string).strip()
            elif html_soup.select("div.head-materia > h2"):
                record["subtitle"] = re.sub(r"\s+", " ",
                    html_soup.select("div.head-materia > h2")[0].string).strip()

            # Authors.
            if html_soup.find("div", class_="article__author"):
                record["author"] = re.sub(r"\s+", " ",
                    html_soup.find("div", class_="article__author").string).strip()
            elif html_soup.find("span", class_="autor"):
                record["author"] = re.sub(r"\s+", " ",
                    html_soup.find("span", class_="autor").string).strip()

            # Date of Publication.
            if html_soup.find("div", class_="article__date"):
                record["date"] = re.sub(r"\s+", " ",
                    html_soup.find("div", class_="article__date").string).strip()
            elif html_soup.find("div", class_="meta-data"):
                record["date"] = re.sub(r"\s+", " ",
                    html_soup.find("div", class_="meta-data").text).strip()

            # Full text.
            if html_soup.select("main.main-content > p"):
                record["text"] = re.sub(r"\s+", " ", " ".join(
                    [tag_p.text for tag_p in html_soup.select("main.main-content > p")])).strip()
            elif html_soup.find_all("div", class_="capituloPage"):
                record["text"] = re.sub(r"\s+", " ", " ".join(
                    [tag_p.text for tag_div in html_soup.find_all("div", class_="capituloPage")
                        for tag_p in tag_div.find_all("p", recursive=True)])).strip()

            data.append(record)
        except Exception as e:
            print(idx)
            raise e

    # Closing the PhantomJS webdriver.
    driver.quit()

    return data


# Method to define the rumor's classification.
def set_classification(title):
    if "#FAKE" in title and "#FATO" not in title:
        return 1
    elif "#FAKE" not in title and "#FATO" in title:
        return 0
    else:
        return None


########################################################################
# 2. Getting the data from its URL
########################################################################

# Determining the URL of target page.
url = "https://oglobo.globo.com/fato-ou-fake/"

# Collecting the news URLs.
links = list(set(get_links(url)))

# Printing the number of links collected.
print("Number of links collected: {}.".format(len(links)))

# Saving the backup of news URLs.
with open("links_bkp.txt", "w") as file:
    file.writelines([link + "\n" for link in links])

# Collecting the data.
data = get_data(url, links)

# Printing the number of records collected.
print("Number of records collected: {}.".format(len(data)))

########################################################################
# 3. Saving the data collected
########################################################################

# Creating the dataframe object.
df_data = pd.DataFrame(data)

# Creating new features.
df_data["id"] = df_data.index.values + 1
df_data["link"] = links
df_data["classification"] = df_data.title.apply(set_classification)

# Changing the type of "classification" column.
df_data.classification.loc[
    df_data.classification.notnull()] = df_data.classification.loc[
        df_data.classification.notnull()].astype(np.int64)

# Sorting the columns.
df_data = df_data[
    ["id", "link", "date", "title", "subtitle", "text", "author",
     "classification"]
]

# Checking the information about the dataset.
print(df_data.info())

# Exporting the data to CSV file.
df_data.to_csv("o_globo_fato_fake.csv",
    index=False, quoting=csv.QUOTE_ALL)
