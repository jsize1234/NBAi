from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import subprocess

def scrape_with_selenium(url):
    driver_path = "C:\\WebDrivers\\chromedriver.exe"

    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Use updated headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        # Wait for the specific dropdown parent to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Pagination_pageDropdown__KgjBU"))
        )

        # Locate the specific dropdown by finding its parent first
        dropdown_parent = driver.find_element(By.CLASS_NAME, "Pagination_pageDropdown__KgjBU")
        dropdown = dropdown_parent.find_element(By.CLASS_NAME, "DropDown_select__4pIg9")

        # Use Select to interact with the dropdown
        select = Select(dropdown)

        # Debugging: Print all available options
        # for option in select.options:
            # print(f"Option text: {option.text}, value: {option.get_attribute('value')}")

        # Select "All" using the value "-1"
        select.select_by_value("-1")

        # Wait for the full table to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Crom_body__UYOcU"))
        )

        # Get the page source after loading all players
        html_content = driver.page_source

    except Exception as e:
        print(f"Error: {e}")
        html_content = ""
    finally:
        driver.quit()

    return html_content

def parse_scrape_with_bs4(html_content, season):
    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.find('tbody', class_="Crom_body__UYOcU")

    player_data = []

    rows = table.select('tr')

    for row in rows:
        player_info = row.find_all('td')
        player_name = player_info[0].text.strip()
        team = player_info[1].text.strip()
        age = player_info[2].text.strip()
        height = player_info[3].text.strip()
        weight = player_info[4].text.strip()
        college = player_info[5].text.strip()
        country = player_info[6].text.strip()
        draft_year = player_info[7].text.strip()
        draft_round = player_info[8].text.strip()
        draft_number = player_info[9].text.strip()


        player_link = player_info[0].find('a')['href']
        player_id = player_link.split('/')[-2]

        player_data.append({
            'Season' : season,
            'Player Name' : player_name,
            'NBA Player ID' : player_id,
            'Team' : team,
            'Age' : age,
            'Height' : height,
            'Weight' : weight,
            'College' : college,
            'Country' : country,
            'Draft Year' : draft_year,
            'Draft Round' : draft_round,
            'Draft Number' : draft_number,
        })
    return pd.DataFrame(player_data)


def generate_year_ranges(start_year, end_year):
    ranges = []
    for year in range(start_year, end_year):
        range_str = f"{year}-{str(year + 1)[-2:]}"
        ranges.append(range_str)
    return ranges

def scrape_multiple_seasons(start_year, end_year, base_url):
    year_ranges = generate_year_ranges(start_year, end_year)
    all_player_data = pd.DataFrame()
    response_count = 0

    for season in year_ranges:
        print(f"Scraping data for season: {season}")
        url = f"{base_url}?Season={season}"
        html = scrape_with_selenium(url)
        if html:
            season_data = parse_scrape_with_bs4(html, season)
            all_player_data = pd.concat([all_player_data, season_data], ignore_index=True)
        response_count += 1
        if response_count % 25 == 0:
            change_ip()
    
    return all_player_data

def change_ip():
    try:
        print("Disconnecting from previous VPN location")
        disconnect_result = subprocess.run(["mullvad", "disconnect"], capture_output=True, text=True)
        if disconnect_result.returncode ==0:
            print("VPN disconnected successfully")
        else:
            print(f"Failed to disconnect from VPN, make sure you are connected before running the script")
            return
        time.sleep(2)

        
        print("Ensuring correct relay is set via Mullvad")
        relay_result = subprocess.run(["mullvad", "relay", "set", "location", "us"], capture_output=True, text=True)
        if relay_result.returncode == 0:
            print("IP changed successfully")
        else:
            print(f"Failed to change IP: {relay_result.stderr}")


        print("Connecting to new IP")
        connect_result = subprocess.run(["mullvad", "connect"], capture_output=True, text=True)
        if connect_result.returncode == 0:
            print("IP successfully changed")
        else:
            print(f"Failed to change IP: {connect_result.stderr}")
            return
        time.sleep(5)


    except Exception as e:
        print(f"Error while changing IP: {e}")

start_year = 1996
end_year = 2025
base_url = "https://www.nba.com/stats/players/bio"

all_player_info = scrape_multiple_seasons(start_year, end_year, base_url)

all_player_info.to_csv("nba_player_data.csv", index=False, encoding="utf-8")

print("Data for year range is scraped and saved to csv.")