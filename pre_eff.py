import pandas as pd
import os


def process_sequence(file_path, threshold):
    rows = []
    with open(file_path, 'r') as file:
        for line in file:
            row = line.strip().split('\t')
            rows.append(row)

    start_index = [i for i, row in enumerate(rows) if '@data' in row][0]
    data = rows[start_index + 1:]
    data_df = pd.DataFrame(data)
    activity_counts = data_df[4].value_counts()
    filtered_activities = activity_counts[activity_counts >= threshold].index.tolist()
    filtered = data_df[data_df[4].isin(filtered_activities)]
    filtered_df = filtered.drop_duplicates()
    hand = "Right hand" if "R" in file_path else "Left hand"
    variable = ["Hand", "ObjectActedOn", "ObjectInHand", "HandState", "Activity"]
    filtered_df.columns = variable
    # print(f"{hand} sequence for {os.path.basename(file_path)}:\n", filtered_df[4])
    print(f"{hand} sequence:\n", filtered_df)


path = "data/task_graph/2023-11-27-15-09-22"
file_names = ["data4testing_R.txt", "data4testing_L.txt"]
threshold = 150
for file_name in file_names:
    file_path = os.path.join(path, file_name)
    process_sequence(file_path, threshold)
