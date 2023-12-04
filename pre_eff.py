import os
import pandas as pd


def update_dict(dict1, dict2):
    return {k: v for k, v in dict1.items() if dict2.get(k) == v}


def read_data(file_path, threshold):
    with open(file_path, 'r') as file:
        line = file.readlines()
    start_index = line.index('@data\n') + 1
    data_lines = line[start_index:]
    df = pd.DataFrame([line.strip().split('\t') for line in data_lines if line.strip() != ''],
                      columns=['Hand', 'ObjectActedOn', 'ObjectInHand', 'HandState', 'Activity'])
    activity_counts = df['Activity'].value_counts()
    filtered_activities = activity_counts[activity_counts >= threshold].index.tolist()
    filtered_df = df[df['Activity'].isin(filtered_activities)]
    return filtered_df


def only_idlemotion(file_path, threshold):
    filtered_df = read_data(file_path, threshold)
    return set(filtered_df['Activity']) == {'IdleMotion'}


def process_sequence(file_path, threshold):
    filtered_df = read_data(file_path, threshold)
    sequence = filtered_df.loc[(filtered_df.shift() != filtered_df).any(axis=1)]
    sequence = extract(sequence)
    # hand = "Right hand" if "R" in file_path else "Left hand"
    # print(f"{hand} sequence:\n", sequence)
    return sequence


def extract(df):
    activities = df['Activity']
    buffer = {}
    for activity in activities:
        activity_df = df[df['Activity'] == activity]
        precondition = activity_df.iloc[0][0:4].to_dict()
        effect = activity_df.iloc[-1][0:4].to_dict()
        if activity not in buffer:
            buffer[activity] = {
                'precondition': precondition,
                'effect': effect
            }
        else:
            previous_precondition = buffer[activity]['precondition']
            previous_effect = buffer[activity]['effect']
            updated_precondition = update_dict(previous_precondition, precondition)
            updated_effect = update_dict(previous_effect, effect)
            buffer[activity] = {
                'precondition': updated_precondition,
                'effect': updated_effect
            }
    return buffer


def merge(path, threshold):
    all_activities = {}
    for file_name in ['data4testing_R.txt', 'data4testing_L.txt']:
        file_path = os.path.join(path, file_name)
        if not only_idlemotion(file_path, threshold):
            activities = process_sequence(file_path, threshold)
            for activity, details in activities.items():
                if activity not in all_activities:
                    all_activities[activity] = details
                else:
                    existing_precondition = all_activities[activity]['precondition']
                    existing_effect = all_activities[activity]['effect']
                    updated_precondition = update_dict(existing_precondition, details['precondition'])
                    updated_effect = update_dict(existing_effect, details['effect'])
                    all_activities[activity] = {
                        'precondition': updated_precondition,
                        'effect': updated_effect
                    }
    return all_activities


path = 'data/task_graph/2023-11-27-15-09-22'
threshold = 30
rich_info = merge(path, threshold)
print(rich_info)


