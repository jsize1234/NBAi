from bs4 import BeautifulSoup, Comment
import pandas as pd
import requests
import re
from datetime import datetime
import subprocess
import time


def shot_data(player_name, url):
    url = url.replace(".html", "/shooting/2025")
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                print(f"Successfully fetched data for {player_name} on attempt {attempt+1}")
                html_content = response.text
                break
            else:
                print(f"Attempt {attempt + 1} failed with the status code {response.status_code}. Changing IP...")
                change_ip()
        
        except requests.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries -1:
                print("Changing IP and retrying...")
                change_ip()
            else:
                print(f"Reached 3 retries. Skipping {player_name}")
                return pd.DataFrame()
    
    else:
        return pd.DataFrame()


    soup = BeautifulSoup(html_content, 'html.parser')

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    shot_data_dataframe = []

    for comment in comments:
        if "shot-area" in comment:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            shot_area = comment_soup.find('div', class_="shot-area")

            if shot_area:
                for row in shot_area.find_all('div', style=True, tip=True):
                    style = row['style']
                    tip = row['tip']
                    
                    # Get the x_coordinate in pixel format
                    pixel_x_coordinate_match = re.search(r'left:([\-]?\d+)px;', style)
                    pixel_x_coordinate = int(pixel_x_coordinate_match.group(1)) if pixel_x_coordinate_match else None

                    # Get the y_coordinate in pixel format
                    pixel_y_coordinate_match = re.search(r'top:([\-]?\d+)px;', style)
                    pixel_y_coordinate = int(pixel_y_coordinate_match.group(1)) if pixel_y_coordinate_match else None

                    # Court image dimensions
                    court_width = 500
                    court_height = 472
                    court_center_x = court_width / 2

                    # Get normalized x and y values
                    X_LOC = -((pixel_x_coordinate - court_center_x) / court_center_x) * 25
                    Y_LOC = (pixel_y_coordinate / court_height) * 47.5
                    
                    # Get the date the game happened
                    date_match = re.search(r'(\w{3} \d{1,2}, \d{4})', tip)
                    game_date = None
                    if date_match:
                        date_str = date_match.group(1)
                        game_date = datetime.strptime(date_str, "%b %d, %Y").strftime("%m-%d-%Y")
                    
                    # Get the home and away teams
                    teams_match = re.search(r'(\w{3})\s(vs|at)\s(\w{3})', tip)
                    home_team, away_team = None, None
                    if teams_match:
                        team1, game_location, team2 = teams_match.groups()
                        if game_location == "vs":
                            home_team, away_team = team1, team2
                        elif game_location == "at":
                            home_team, away_team = team2, team1
                    
                    # Get quarter
                    quarter_match = re.search(r'(\d{1})(?:st|nd|rd|th)\sQtr', tip)
                    overtime_match = re.search(r'(\d{1})(?:st|nd|rd|th)\sOT', tip)
                    quarter = None
                    if quarter_match:
                        quarter = int(quarter_match.group(1))
                    elif overtime_match:
                        quarter = 4 + int(overtime_match.group(1))
                    
                    # Get remaining minutes and seconds
                    time_remaining_match = re.search(r'(\d{1,2}):(\d{2})\sremaining', tip)
                    minutes_remaining = int(time_remaining_match.group(1)) if time_remaining_match else None
                    seconds_remaining = int(time_remaining_match.group(2)) if time_remaining_match else None
                
                    # Shot made or missed
                    shot_made_or_missed = "Made" if "Made" in tip else "Missed"

                    # Get shot type (2pt or 3pt)
                    shot_type_match = re.search(r'(2|3)-pointer', tip)
                    shot_type = f"{shot_type_match.group(1)}pt" if shot_type_match else None

                    # Get distance from basket
                    distance_match = re.search(r'from\s(\d+)\sft', tip)
                    distance_from_basket = int(distance_match.group(1)) if distance_match else None

                    # Get current score
                    score_match = re.search(r'(\d+)-(\d+)', tip)
                    current_score = f"{score_match.group(1)}-{score_match.group(2)}" if score_match else None

                    # Get team who is winning at the moment
                    if score_match:
                        score1, score2 = int(score_match.group(1)), int(score_match.group(2))
                        if score1 > score2:
                            leading_team = home_team
                        elif score1 < score2:
                            leading_team = away_team
                        else:
                            leading_team = "Tied"
                    else:
                        leading_team = None
            
                    # Add data to the shot data dataframe
                    shot_data_dataframe.append({
                        'Player Name' : player_name,
                        'Player Shooting Link' : url,
                        'X_LOC' : X_LOC,
                        'Y_LOC' : Y_LOC,
                        'Game Date' : game_date,
                        'Home Team' : home_team,
                        'Away Team' : away_team,
                        'Quarter' : quarter,
                        'Minutes Remaining' : minutes_remaining,
                        'Seconds Remaining' : seconds_remaining,
                        'Shot Made or Missed' : shot_made_or_missed,
                        'Shot Type' : shot_type,
                        'Distance' : distance_from_basket,
                        'Current Score' : current_score,
                        'Leading Team' : leading_team,
                    })
    
    return pd.DataFrame(shot_data_dataframe)


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

        
        #print("Ensuring correct relay is set via Mullvad")
        #relay_result = subprocess.run(["mullvad", "relay", "set", "location", "us"], capture_output=True, text=True)
        #if relay_result.returncode == 0:
            #print("IP changed successfully")
        #else:
            #print(f"Failed to change IP: {relay_result.stderr}")


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

                    
def player_shot_data_scrape(unique_data):
    player_shot_data = []

    response_count = 0

    for index, row in unique_data.iterrows():
        player_name = row.get('Player Name', 'Unknown Player')
        player_link = row.get('Player Link', None)

        # Skip rows with invalid or NaN URLs
        if not isinstance(player_link, str) or pd.isna(player_link):
            print(f"Skipping {player_name} due to invalid or missing URL.")
            continue

        # Process valid URLs
        scrape_player_shot_data = shot_data(player_name, player_link)
        if not scrape_player_shot_data.empty:
            player_shot_data.append(scrape_player_shot_data)

        response_count += 1
        if response_count % 20 == 0:
            change_ip()

    # Combine all DataFrames in the list
    if player_shot_data:
        return pd.concat(player_shot_data, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no valid data was found




file_path = r"C:\Users\joeys\Documents\Python Scripts\NBAi Web Scraping\2024-25_unique_data.csv"

unique_data = pd.read_csv(file_path)

shot_data_for_2025 = player_shot_data_scrape(unique_data)
shot_data_for_2025.to_csv('2025_shot_data.csv', index=False, encoding='utf-8')