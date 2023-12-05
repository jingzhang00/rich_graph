import os
import pandas as pd


def flatten_and_unique(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_and_unique(item))
        else:
            result.append(item)
    return list(set(result))


def update_dict(dict1, dict2):
    result = {}
    all_keys = set(dict1).union(set(dict2))
    for key in all_keys:
        values = []
        if key in dict1:
            values.append(dict1[key])
        if key in dict2:
            values.append(dict2[key])
        result[key] = values
    return result


def simplify_dict(dict1, dict2):
    combined_dict = update_dict(dict1, dict2)
    return {k: flatten_and_unique(v) for k, v in combined_dict.items()}


def extract(df):
    activities = df['Activity']
    last_non_idle_index = (activities != 'IdleMotion').to_numpy().nonzero()[0][-1]
    if last_non_idle_index < len(activities) - 1:
        df = df.iloc[:last_non_idle_index + 1]
    df = df.reset_index(drop=True)
    buffer = {}
    last_activity = None
    start_index = 0
    activities = activities.reset_index(drop=True)
    for index, activity in activities.items():
        if activity != last_activity:
            if last_activity is not None:
                activity_df = df.iloc[start_index:index]
                precondition = activity_df.iloc[0][0:4].to_dict()
                effect = activity_df.iloc[-1][0:4].to_dict()
                if last_activity not in buffer:
                    buffer[last_activity] = {
                        'precondition': precondition,
                        'effect': effect
                    }
                else:
                    previous_precondition = buffer[last_activity]['precondition']
                    previous_effect = buffer[last_activity]['effect']
                    updated_precondition = simplify_dict(previous_precondition, precondition)
                    updated_effect = simplify_dict(previous_effect, effect)
                    buffer[last_activity] = {
                        'precondition': updated_precondition,
                        'effect': updated_effect
                    }
            last_activity = activity
            start_index = index
    return buffer



class ActivityProcessor:
    def __init__(self, path, threshold):
        self.path = path
        self.threshold = threshold
        self.rich_info = self.merge()

    def read_data(self, file_path):
        with open(file_path, 'r') as file:
            line = file.readlines()
        start_index = line.index('@data\n') + 1
        data_lines = line[start_index:]
        df = pd.DataFrame([line.strip().split('\t') for line in data_lines if line.strip() != ''],
                          columns=['Hand', 'ObjectActedOn', 'ObjectInHand', 'HandState', 'Activity'])
        activity_counts = df['Activity'].value_counts()
        filtered_activities = activity_counts[activity_counts >= self.threshold].index.tolist()
        filtered_df = df[df['Activity'].isin(filtered_activities)].copy()
        filtered_df.loc[filtered_df['ObjectInHand'] == 'Main Camera', 'ObjectInHand'] = 'NONE'
        filtered_df.loc[filtered_df['ObjectActedOn'] != 'NONE', 'ObjectActedOn'] = 'Something'
        filtered_df.loc[filtered_df['Hand'] == 'ToolUse', 'Hand'] = 'Moving'
        filtered_df.loc[filtered_df['Hand'] == 'Move', 'Hand'] = 'Moving'
        return filtered_df

    def only_idlemotion(self, file_path):
        filtered_df = self.read_data(file_path)
        return set(filtered_df['Activity']) == {'IdleMotion'}

    def process_sequence(self, file_path):
        filtered_df = self.read_data(file_path)
        sequence = filtered_df.loc[(filtered_df.shift() != filtered_df).any(axis=1)]
        sequence = extract(sequence)
        return sequence

    def merge(self):
        buffer = {}
        for file_name in ['data4testing_R.txt', 'data4testing_L.txt']:
            file_path = os.path.join(self.path, file_name)
            if not self.only_idlemotion(file_path):
                dicts = self.process_sequence(file_path)
                for activity, info in dicts.items():
                    if activity not in buffer:
                        buffer[activity] = info
                    else:
                        existing_precondition = buffer[activity]['precondition']
                        existing_effect = buffer[activity]['effect']
                        updated_precondition = simplify_dict(existing_precondition, info['precondition'])
                        updated_effect = simplify_dict(existing_effect, info['effect'])
                        buffer[activity] = {
                            'precondition': updated_precondition,
                            'effect': updated_effect
                        }
        return buffer


if __name__ == "__main__":
    path = 'data/task_graph/multiple_demos'
    threshold = 30
    processor = ActivityProcessor(path, threshold)
    rich_info = processor.rich_info
    print(rich_info)
