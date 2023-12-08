import os
import pandas as pd
import pprint


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


def filter_data(df, threshold):
    activity_idx = []
    last_activity = None
    remove_indices = []
    for index, row in df.iterrows():
        current_activity = row['Activity']
        if current_activity != last_activity:
            activity_idx.append(index)
            last_activity = current_activity
    for i in range(len(activity_idx) - 1):
        if activity_idx[i + 1] - activity_idx[i] < threshold:
            remove_indices.extend(range(activity_idx[i], activity_idx[i + 1]))
    mask = ~df.index.isin(remove_indices)
    df = df[mask]

    non_idle_indices = df[df['Activity'] != 'IdleMotion'].index
    if len(non_idle_indices) == 0:
        return df
    first_non_idle = non_idle_indices[0]
    last_non_idle = non_idle_indices[-1]
    start_df = df.iloc[:first_non_idle]
    middle_df = df.iloc[first_non_idle:last_non_idle + 1]
    middle_df = middle_df[middle_df['Activity'] != 'IdleMotion']
    end_df = df.iloc[last_non_idle:]
    filtered_df = pd.concat([start_df, middle_df, end_df])
    return filtered_df.reset_index(drop=True)


def extract(df, threshold):
    df_filter = filter_data(df, threshold)
    df_filter.reset_index(drop=True)
    buffer = {}
    last_activity = None
    start_index = 0

    for index, activity in enumerate(df_filter['Activity']):
        if activity != last_activity:
            if last_activity is not None:
                activity_df = df_filter.iloc[start_index:index]
                precondition = activity_df.iloc[0][0:4].to_dict()
                effect = activity_df.iloc[-1][0:4].to_dict()

                if last_activity in buffer:
                    buffer[last_activity]['precondition'] = simplify_dict(buffer[last_activity]['precondition'],
                                                                          precondition)
                    buffer[last_activity]['effect'] = simplify_dict(buffer[last_activity]['effect'], effect)
                else:
                    buffer[last_activity] = {
                        'precondition': precondition,
                        'effect': effect
                    }
            start_index = index
            last_activity = activity

    if last_activity is not None:
        activity_df = df_filter.iloc[start_index:]
        precondition = activity_df.iloc[0][0:4].to_dict()
        effect = activity_df.iloc[-1][0:4].to_dict()

        if last_activity in buffer:
            buffer[last_activity]['precondition'] = simplify_dict(buffer[last_activity]['precondition'], precondition)
            buffer[last_activity]['effect'] = simplify_dict(buffer[last_activity]['effect'], effect)
        else:
            buffer[last_activity] = {
                'precondition': precondition,
                'effect': effect
            }
    return buffer


class ActivityProcessor:
    def __init__(self, path, threshold=20):
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
        df.loc[df['ObjectInHand'] == 'Main Camera', 'ObjectInHand'] = 'NONE'
        return df

    def only_idlemotion(self, file_path):
        filtered_df = self.read_data(file_path)
        return set(filtered_df['Activity']) == {'IdleMotion'}

    def process_sequence(self, file_path):
        filtered_df = self.read_data(file_path)
        sequence = filtered_df.loc[(filtered_df.shift() != filtered_df).any(axis=1)]
        sequence = extract(sequence, self.threshold)
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
    threshold = 20
    processor = ActivityProcessor(path, threshold)
    rich_info = processor.rich_info
    pprint.pprint(rich_info, width=80, compact=True)
