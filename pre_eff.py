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
    remove_indices = []
    last_index = None
    for index, row in df.iterrows():
        if last_index is not None and index - last_index < threshold:
            remove_indices.append(last_index)
        last_index = index

    activity_idx = []
    last_activity = None

    for index, row in df.iterrows():
        current_activity = row['Activity']
        if current_activity != last_activity:
            activity_idx.append(index)
            last_activity = current_activity

    for i in range(1, len(activity_idx) - 1):
        current_index = activity_idx[i]
        previous_index = activity_idx[i - 1]
        next_index = activity_idx[i + 1]
        if df.at[current_index, 'Activity'] == 'IdleMotion':
            if df.at[previous_index, 'Activity'] == df.at[next_index, 'Activity']:
                remove_indices.extend(df.loc[current_index:next_index].index)

    mask = ~df.index.isin(remove_indices)
    df = df[mask]
    return df.reset_index(drop=True)


def extract(df, threshold):
    df_filter = filter_data(df, threshold)
    df_filter.reset_index(drop=True)
    buffer = {}
    last_activity = None
    start_index = 0

    for index, activity in enumerate(df_filter['Activity']):
        if activity != last_activity:
            if last_activity is not None:
                current_activity_df = df_filter.iloc[start_index:index]
                precondition = current_activity_df.iloc[0][0:4].to_dict()
                next_activity_start = index if index < len(df_filter) else None

                if last_activity in buffer:
                    buffer[last_activity]['precondition'] = simplify_dict(buffer[last_activity]['precondition'],
                                                                          precondition)
                    if next_activity_start is not None:
                        next_activity_df = df_filter.iloc[next_activity_start:next_activity_start + 1]
                        effect = next_activity_df.iloc[0][0:4].to_dict()
                        buffer[last_activity]['effect'] = simplify_dict(buffer[last_activity]['effect'], effect)
                else:
                    next_activity_df = df_filter.iloc[next_activity_start:next_activity_start + 1]
                    effect = next_activity_df.iloc[0][0:4].to_dict()

                    buffer[last_activity] = {
                        'precondition': precondition,
                        'effect': effect
                    }
            start_index = index
            last_activity = activity

    if last_activity is not None:
        activity_df = df_filter.iloc[start_index:]
        precondition = activity_df.iloc[0][0:4].to_dict()

        if last_activity in buffer:
            buffer[last_activity]['precondition'] = simplify_dict(buffer[last_activity]['precondition'], precondition)
        else:
            buffer[last_activity] = {
                'precondition': precondition,
                'effect': {}
            }
    return buffer


def read_data(file_path):
    with open(file_path, 'r') as file:
        line = file.readlines()
    start_index = line.index('@data\n') + 1
    data_lines = line[start_index:]
    df = pd.DataFrame([line.strip().split('\t') for line in data_lines if line.strip() != ''],
                      columns=['Hand', 'ObjectActedOn', 'ObjectInHand', 'HandState', 'Activity'])
    df.loc[df['ObjectInHand'] == 'Main Camera', 'ObjectInHand'] = 'NONE'
    return df


def only_idlemotion(file_path):
    filtered_df = read_data(file_path)
    return set(filtered_df['Activity']) == {'IdleMotion'}


class ActivityProcessor:
    def __init__(self, path, threshold=20):
        self.path = path
        self.threshold = threshold
        self.rich_info = self.merge()

    def process_sequence(self, file_path):
        filtered_df = read_data(file_path)
        sequence = filtered_df.loc[(filtered_df.shift() != filtered_df).any(axis=1)]
        sequence = sequence[sequence['Activity'] != 'UnknownActivity']
        sequence = extract(sequence, self.threshold)
        return sequence

    def merge(self):
        buffer = {}
        for file_name in ['data4testing_R.txt', 'data4testing_L.txt']:
            file_path = os.path.join(self.path, file_name)
            if not only_idlemotion(file_path):
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
    path = 'data/13_demos'
    threshold = 15
    processor = ActivityProcessor(path, threshold)
    rich_info = processor.rich_info
    pprint.pprint(rich_info, width=80, compact=True)
