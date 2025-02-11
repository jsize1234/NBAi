# **NBAi - AI-Powered NBA Data Analysis & Shot Prediction**

## **📌 Overview**
NBAi is a **data-driven basketball analytics tool** that leverages **machine learning, web scraping, and visualization** to analyze player performance, shot accuracy, and game statistics. This project automates the extraction of **NBA player data, schedules, and shooting stats**, making it ideal for sports analysts, data scientists, and basketball enthusiasts.

## **🚀 Features**
✅ **Automated Web Scraping**: Collects real-time and historical NBA data using Selenium & BeautifulSoup.

✅ **Data Processing & ETL**: Cleans, structures, and transforms data into actionable insights.

✅ **Shot Location Visualization**: Maps successful vs. missed shots on an NBA court using Matplotlib & PIL.

✅ **Game Schedule Analysis**: Extracts, processes, and stores NBA schedules for trend analysis.

✅ **VPN IP Rotation**: Uses Mullvad VPN CLI to avoid anti-scraping blocks.

✅ **Machine Learning-Ready Datasets**: Prepares structured data for AI-based predictive modeling.

## **📂 Project Structure**
```
NBAi/
│── data/                      # Contains CSV datasets (players, shots, schedules)
│── notebooks/                 # Jupyter Notebooks for data analysis & visualization
│── scripts/                   # Python scripts for scraping, processing & visualization
│   ├── game_data_current_regular_season.py   # Scrapes NBA schedule
│   ├── player_data.py                        # Scrapes player statistics
│   ├── player_data_by_season_nba.py          # Extracts player bio data
│   ├── shot_data_by_player.py                # Collects shot attempts & success rates
│   ├── graph_shot_test.py                    # Generates shot location visualizations
│── requirements.txt          # Dependencies
│── README.md                 # Project documentation
```

## **⚙️ Installation**
### **Prerequisites**
Ensure you have the following installed:
- Python 3.8+
- Chrome WebDriver (for Selenium scraping)
- Mullvad VPN (optional for IP rotation)

### **Setup**
1. **Clone the repository**
```sh
git clone https://github.com/yourusername/NBAi.git
cd NBAi
```

2. **Install dependencies**
```sh
pip install -r requirements.txt
```

3. **Setup WebDriver (for Selenium)**
   - Download **chromedriver.exe** and place it in `C:\WebDrivers\chromedriver.exe`
   - Or update the script with your WebDriver path

## **🛠️ Usage**
### **1️⃣ Scrape NBA Game Schedule**
```sh
python scripts/game_data_current_regular_season.py
```
- This will extract and save **NBA schedule data** into `nba_schedule_2024_25.csv`

### **2️⃣ Scrape Player Stats**
```sh
python scripts/player_data.py
```
- This script fetches player details from Basketball-Reference

### **3️⃣ Scrape Shot Data**
```sh
python scripts/shot_data_by_player.py
```
- Collects **shot attempt locations & outcomes**

### **4️⃣ Visualize Shot Charts**
```sh
python scripts/graph_shot_test.py
```
- Generates **shot location maps** on a court diagram

## **🔮 Future Improvements**
- ✅ **Machine Learning Shot Prediction**
- ✅ **Team & Player Performance Trends**
- ✅ **Interactive Web Dashboard** (Streamlit or Flask)
- ✅ **API Integration** for real-time updates

