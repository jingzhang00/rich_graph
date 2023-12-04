import os
import pandas as pd


def process_sequence(file_path, threshold):
    with open(file_path, 'r') as file:
        line = file.readlines()
    start_index = line.index('@data\n') + 1
    data_lines = line[start_index:]
    df = pd.DataFrame([line.strip().split('\t') for line in data_lines if line.strip() != ''],
                      columns=['Hand', 'ObjectActedOn', 'ObjectInHand', 'HandState', 'Activity'])
    activity_counts = df['Activity'].value_counts()
    filtered_activities = activity_counts[activity_counts >= threshold].index.tolist()
    sequence = df[df['Activity'].isin(filtered_activities)]
    sequence = sequence.loc[(sequence.shift() != sequence).any(axis=1)]
    sequence = filter_sequence(sequence)
    hand = "Right hand" if "R" in file_path else "Left hand"
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(f"{hand} sequence:\n", sequence)
    return sequence


def filter_sequence(df, ignore_activity='IdleMotion'):
    filtered_rows = []
    idle_motion_seen = False
    is_sequence_start = True
    for index, row in df.iterrows():
        current_activity = row['Activity']
        if current_activity == ignore_activity:
            if is_sequence_start or not idle_motion_seen:
                idle_motion_seen = True
                filtered_rows.append(row)
            continue
        else:

            is_sequence_start = False

        filtered_rows.append(row)
    return pd.DataFrame(filtered_rows)


path = 'data/task_graph/2023-11-27-15-09-22'
threshold = 30
for file_name in ['data4testing_R.txt', 'data4testing_L.txt']:
    file_path = os.path.join(path, file_name)
    sequence = process_sequence(file_path, threshold)
