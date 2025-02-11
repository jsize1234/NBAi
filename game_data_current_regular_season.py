from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
import re

def scrape_with_selenium(url):
    driver_path = "C:\\WebDrivers\\chromedriver.exe"

    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Updated headless mode
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

        # Wait for the initial schedule container to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ScheduleWeek_swBase__6wxQ7"))
        )

        previous_game_count = 0  # Keep track of games loaded
        while True:
            try:
                # Find the "Load More" button
                load_more_button = driver.find_element(By.CLASS_NAME, "Button_button__L2wUb")

                # Scroll into view and click the button
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "Button_button__L2wUb")))
                load_more_button.click()

                # Wait for new content to load
                time.sleep(3)

                # Scroll to the bottom to ensure all new content renders
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            except Exception as e:
                print("No more 'Load More' button to click or an error occurred:", e)
                break

        # Get the page source after all content is loaded
        html_content = driver.page_source
        return html_content

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()


def parse_nba_schedule_with_bs4(html_content, current_season, year_range):
    soup = BeautifulSoup(html_content, 'html.parser')

    start_year, end_year = map(int, current_season.split("-"))

    # Find all weeks
    weeks = soup.find_all("div", class_="ScheduleWeek_swBase__6wxQ7")
    all_games = []

    for week in weeks:
        # Extract the week header
        week_header = week.find("h2", class_="ScheduleWeek_swHeader__2THvJ").text.strip()

        # Find all days in the week
        days = week.find_all("div", class_="ScheduleDay_sd__GFE_w")

        for day in days:
            # Extract the day header and number of games
            day_header = day.find("h4", class_="ScheduleDay_sdDay__3s2Xt").text.strip()
            #num_games = day.find("h6", class_="ScheduleDay_sdWeek__iiTmo").text.strip()

            # Extract month and day from the day header
            month_day = " ".join(day_header.split(",")[1].split()).strip()  # Extract "October 22"
            month, day_of_month = month_day.split(" ")
            day_of_month = int(day_of_month)

            # Determine the year based on the month
            month_number = datetime.strptime(month, "%B").month  # Convert month name to number
            if month_number <= 12:  # Decembers belong to the start year
                year = start_year if month_number >= 10 else end_year  # Oct, Nov, Dec in start year
            else:
                year = end_year  # Games in Jan to Apr of end year

            # Format the date as MM-DD-YYYY
            formatted_date = f"{month_number:02d}-{day_of_month:02d}-{year}"


            # Find all games for the day
            games = day.find_all("div", class_="ScheduleGame_sg__RmD9I")

            for game in games:
                try:
                    # Extract game status
                    status = game.find("span", class_="ScheduleStatusText_base__Jgvjb")
                    status = status.text.strip() if status else "Scheduled"

                    # Extract teams
                    teams = game.find_all("div", class_="ScheduleGame_sgTeam__TEPZa")

                    # Team 1 details
                    team1 = teams[0].find("a").text.strip()
                    team1_id = teams[0].find("a")["data-content-id"]
                    team1_score = teams[0].find("span", class_="ScheduleGame_sgScoreVal__L4KZO")
                    team1_score = team1_score.text.strip() if team1_score else None

                    # Team 2 details
                    team2 = teams[1].find("a").text.strip()
                    team2_id = teams[1].find("a")["data-content-id"]
                    team2_score = teams[1].find("span", class_="ScheduleGame_sgScoreVal__L4KZO")
                    team2_score = team2_score.text.strip() if team2_score else None

                    # Get winning team
                    if "Final" in status:
                        team1_score = int(float(team1_score)) if team1_score is not None else 0
                        team2_score = int(float(team2_score)) if team2_score is not None else 0

                        if team1_score > team2_score:
                            winning_team = team1
                        elif team2_score > team1_score:
                            winning_team = team2
                        elif team1_score == team2_score:
                            winning_team = "Tied"
                    else:
                        winning_team = None

                    # Extract location (stadium and city/state)
                    location_element = game.find("div", class_="ScheduleGame_sgLocationInner__xxr0Z")
                    if location_element:
                        stadium = location_element.find_all("div")[0].text.strip()
                        city_state = location_element.find_all("div")[1].text.strip()

                        # Ensure only one space between city and state
                        city_state = re.sub(r"\s{2,}", " ", city_state)

                    else:
                        stadium = "TBD"
                        city_state = "TBD"

                    # Extract game ID
                    game_id_element = game.find("a", {"data-id": "nba:schedule:main:game-details:cta"})
                    game_id = game_id_element["data-content-id"] if game_id_element else None

                    # Append game data
                    all_games.append({
                        "season" : current_season,
                        "week": week_header,
                        "day": formatted_date,
                        #"num_games": num_games,
                        "status": status,
                        "team1": team1,
                        "team1_id": team1_id,
                        "team1_score": team1_score,
                        "team2": team2,
                        "team2_id": team2_id,
                        "team2_score": team2_score,
                        "winning_team" : winning_team,
                        "stadium": stadium,
                        "city_state": city_state,
                        "game_id": game_id,
                    })
                except Exception as e:
                    print(f"Error parsing game details: {e}")

    return pd.DataFrame(all_games)


current_season = "2024-25"
year_range = "2024-2025"

url = "https://www.nba.com/schedule?cal=all&pd=false&region=1&season=Regular%20Season"

html_content = scrape_with_selenium(url)

nba_schedule_current_season = parse_nba_schedule_with_bs4(html_content, current_season, year_range)

output_file = "nba_schedule_2024_25.csv"
nba_schedule_current_season.to_csv(output_file, index=False)




""" with open('nba_schedule_output.txt', 'w', encoding='utf-8') as file:
    file.write(nba_games) """