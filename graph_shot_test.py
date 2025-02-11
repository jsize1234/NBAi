import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
import os


file_path = r"C:\Users\joeys\Documents\Python Scripts\NBAi Web Scraping\2025_shot_data.csv"

shot_data_all = pd.read_csv(file_path)

cui_yongxi_shot_data = shot_data_all[(shot_data_all['Player Name'].str.contains("Cui Yongxi", case=False, na=False))]

court_image = Image.open(r"C:\Users\joeys\Downloads\court_top_view.jpg")
rotated_court_image = court_image.rotate(90, expand=True)

x_min, x_max = -25, 25
y_min, y_max = 0, 90

cui_yongxi_made_shots = cui_yongxi_shot_data[(shot_data_all['Shot Made or Missed'].str.contains("Made", case=False, na=False))]
cui_yongxi_missed_shots = cui_yongxi_shot_data[(shot_data_all['Shot Made or Missed'].str.contains("Missed", case=False, na=False))]

plt.figure(figsize=(7,15))

plt.imshow(rotated_court_image, extent=[x_min, x_max, y_min, y_max], zorder=0)

plt.scatter(cui_yongxi_made_shots['X_LOC'], cui_yongxi_made_shots['Y_LOC'], alpha=0.8, color='green', zorder=1)
plt.scatter(cui_yongxi_missed_shots['X_LOC'], cui_yongxi_missed_shots['Y_LOC'], alpha=0.3, color='red', zorder=2)

plt.title("Shot Locations")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")

plt.show()