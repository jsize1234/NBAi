import requests
from bs4 import BeautifulSoup
import pandas as pd
import subprocess
import time
import re
import datetime

def scrape_nba_player_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.encoding  ='utf-8'

            if response.status_code == 200:
                print(f"Successfully fetched data for {year}")
                html_content = response.text
                break
            else:
                print(f"Attempt {attempt + 1} failed for {year} with status code {response.status_code}. Changing IP...")
                change_ip()
            
        except requests.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Changing IP and retrying...")
                change_ip()
            else:
                print(f"Reached 3 retries. Skipping {year}")
                return pd.DataFrame()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Select rows with data-row attribute
    rows = soup.select('tr')

    # Extract data for all rows
    player_data = []

    for row in rows:
        name_tag = row.find('td', {'data-stat': 'name_display'})
        name = name_tag.get_text(strip=True) if name_tag else None
        link = name_tag.find('a')['href'] if name_tag and name_tag.find('a') else None

        player_data.append({
            'player_name': name,
            'player_link': f"https://www.basketball-reference.com{link}" if link else None,
        })

    return pd.DataFrame(player_data)

def player_extra_info(player_url, player_name):
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = requests.get(player_url)
            response.encoding  ='utf-8'

            if response.status_code == 200:
                print(f"Successfully fetched data for {player_name}")
                html_content = response.text
                break
            else:
                print(f"Attempt {attempt + 1} failed for {player_name} with status code {response.status_code}. Changing IP...")
                change_ip()
            
        except requests.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Changing IP and retrying...")
                change_ip()
            else:
                print(f"Reached 3 retries. Skipping {player_name}")
                return pd.DataFrame()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the birthdate element
    birth_date = None
    birth_span = soup.find('span', {'id': 'necro-birth'})   

    # Extract the birthdate from the 'data-birth' attribute
    birth_date = birth_span.get('data-birth') if birth_span else None

    # Extract the team name from the <a> tag
    team_name_strong = soup.find("strong", string="Team")
    if team_name_strong:
        team_name_a = team_name_strong.find_next_sibling('a')
        team_name = team_name_a.get_text(strip=True) if team_name_a else None
    else:
        team_name = "Free Agent / Retired"
    
    # Extract position using CSS selectors
    position = None
    position_p = soup.select_one("p:contains('Position:')")
    if position_p:
        position_text = position_p.get_text(strip=True)
        position_match = re.search(r'Position:\s*([\w\s]+)', position_text)
        position = position_match.group(1).strip() if position_match else None
        print(f"{player_name} plays {position}")

    # Extract handedness using CSS selectors
    handedness = None
    handedness_p = soup.select_one("p:contains('Shoots:')")
    if handedness_p:
        handedness_text = handedness_p.get_text(strip=True)
        handedness_match = re.search(r'Shoots:\s*(\w+)', handedness_text)
        handedness = handedness_match.group(1).strip() if handedness_match else None
        print(f"{player_name} shoots with {handedness}")

        
    
    # Locate the <img> tag within the <div> with class "media-item"
    image_tag = None
    media_item_div = soup.find('div', class_="media-item")
    if media_item_div:
        image_tag = media_item_div.find('img')

    # Extract the image URL from the 'src' attribute
    image_url = image_tag['src'] if image_tag else None

    player_extra_info = []

    player_extra_info.append({
        'player_name' : player_name,
        'player_birthday' : birth_date,
        'player_current_team' : team_name,
        'player_handedness' : handedness,
        'player_position' : position,
        'player_image' : image_url,
    })

    return pd.DataFrame(player_extra_info)

def scrape_and_merge_player_info(years):
    all_data = pd.DataFrame()
    year_response_count = 0
    # Scrape the initial data

    for year in years:
        player_data = scrape_nba_player_data(year)
        all_data = pd.concat([all_data, player_data], ignore_index=True)
        print(all_data.head())
        year_response_count += 1
        if year_response_count % 20 == 0:
            change_ip()

    # Sort and clean data
    all_data = all_data.sort_values(by='player_name')
    all_data = all_data.drop(all_data[all_data['player_name'] == 'League Average'].index)
    all_data_unique = all_data.drop_duplicates().sort_values(by='player_name')

    # Export all_data_unique
    # all_data_unique.to_csv('2024-25_unique_data.csv', index=False, encoding='utf-8')

    # Collect extra info for each player
    extra_player_info_list = []
    response_count = 0
    for _, row in all_data_unique.iterrows():
        if row['player_link']:  # Ensure there's a valid link
            extra_info = player_extra_info(row['player_link'], row['player_name'])
            if extra_info is not None:
                extra_player_info_list.append(extra_info)
            response_count += 1
            if response_count % 20 == 0:
                change_ip()


    # Combine the extra info into a single DataFrame
    if extra_player_info_list:
        extra_info_df = pd.concat(extra_player_info_list, ignore_index=True)
    else:
        extra_info_df = pd.DataFrame()

    # Merge the extra info with the original unique player data
    merged_data = pd.merge(all_data_unique, extra_info_df, on='player_name', how='left')

    return merged_data

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

current_year = datetime.datetime.now().year
years = range(1996, current_year+1)
final_data = scrape_and_merge_player_info(years)
final_data.to_csv('1996-25_player_data_basketball_reference.csv', index=False, encoding='utf-8')
# for year in years:
#     print(f"Scraping data for: {year}")
#     player_data = scrape_nba_player_data(year)
#     all_data.append(player_data)

# all_data.to_csv('all_data.csv', index=False, encoding='utf-8')
# all_data_unique.to_csv('all_data_unique.csv', index=False, encoding='utf-8')