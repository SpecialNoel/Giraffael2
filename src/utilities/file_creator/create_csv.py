# create_csv.py

# .csv: comma separated value files

import csv

data = [["Name", "Age", "City"], ["Alice", 25, "New York"], ["Bob", 30, "Los Angeles"]]
with open("./test_files/example.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)