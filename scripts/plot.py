import pandas as pd
import matplotlib.pyplot as plt

#df = df[['elapsedSeconds', 'distinct500Faults', 'potentialFaults', 'coveredLines', 'coveredBranches', 'covered2xx', 'notExecutedSeededTests', 'coveredTargets', 'numberOfLines', 
#         'notExecutedSeededTests', 'searchTimeCoveredLines']]


def preprocess_data(data, metric, interval):
    data = data.drop_duplicates(subset=['elapsedSeconds'], keep='first')
    all_seconds = pd.DataFrame({'elapsedSeconds': range(int(data['elapsedSeconds'].min()), int(data['elapsedSeconds'].max()) + 1)})
    data = all_seconds.merge(data, on='elapsedSeconds', how='left')
    data[metric].fillna(method='ffill', inplace=True)
    time_interval = (data['elapsedSeconds'] // interval) * interval
    data = pd.concat([data, time_interval.rename('time_interval')], axis=1)
    return data

def load_and_average(sutname, runs, seeded, metric="coveredTargets", devisor=None, interval=5):
    data_list = []
    for runnr in runs:
        try:
            file_path = f"results/{sutname}/{'seeded' if seeded else 'unseeded'}/run{runnr}/run{runnr}.csv"
            data = pd.read_csv(file_path)
            if seeded:
                data = data[data["notExecutedSeededTests"] == 0]
            if devisor:
                data[metric] = data[metric] / data[devisor].replace(0, float('nan'))

            data['to_plot'] = data[metric]
            data = preprocess_data(data, 'to_plot', interval)
            data_list.append(data[['elapsedSeconds', 'time_interval', 'to_plot']])
        except FileNotFoundError:
            print(f"Warning: File not found for run {runnr}.")
    
    if not data_list:
        return None

    combined_data = pd.concat(data_list, ignore_index=True)
    combined_data = combined_data.groupby(['elapsedSeconds', 'time_interval']).mean().reset_index()

    return combined_data

def truncate_dataframes_to_elapsed_second(elapsed_second, *dataframes):
    truncated_dfs = []
    for df in dataframes:
        if df is not None:
            truncated_dfs.append(df[df['elapsedSeconds'] <= elapsed_second])
        else:
            truncated_dfs.append(None)
    return truncated_dfs

def calculate_growth_percentage(data, exact_second):
    if data is None or data.empty:
        return None

    if exact_second not in data['elapsedSeconds'].values:
        exact_second = data[data['elapsedSeconds'] <= exact_second]['elapsedSeconds'].max()

    data_percentage_point = data[data['elapsedSeconds'] == exact_second].iloc[0]
    data_last = data.iloc[-1]

    growth_percentage = ((data_last['to_plot'] - data_percentage_point['to_plot']) / data_percentage_point['to_plot']) * 100
    return growth_percentage

def get_last_metric_value(data, metric):
    if data is None or data.empty:
        return None
    return data.iloc[-1][metric]

def plot_average_and_calculate_growth(sutname, runs_seeded, runs_unseeded, metric="coveredTargets", devisor=None, interval=5, percentage_point=40, last_elapsed_second=None):
    seeded_data = load_and_average(sutname, runs_seeded, seeded=True, metric=metric, devisor=devisor, interval=interval)
    unseeded_data = load_and_average(sutname, runs_unseeded, seeded=False, metric=metric, devisor=devisor, interval=interval)

    if seeded_data is None and unseeded_data is None:
        print("Error: No data found for plotting.")
        return {}

    if last_elapsed_second is not None:
        seeded_data, unseeded_data = truncate_dataframes_to_elapsed_second(last_elapsed_second, seeded_data, unseeded_data)

    common_max_time = min(seeded_data['elapsedSeconds'].max() if seeded_data is not None else float('inf'),
                          unseeded_data['elapsedSeconds'].max() if unseeded_data is not None else float('inf'))
    exact_second = int(common_max_time * percentage_point / 100)

    growth_dict = {}
    if seeded_data is not None:
        growth_dict['seeded'] = calculate_growth_percentage(seeded_data, exact_second)
    if unseeded_data is not None:
        growth_dict['unseeded'] = calculate_growth_percentage(unseeded_data, exact_second)

    plt.rcParams.update({'font.size': 25,
                         'axes.titlesize': 25,
                         'axes.labelsize': 25,
                         'xtick.labelsize': 25,
                         'ytick.labelsize': 25,
                         'legend.fontsize': 25,
                         'figure.titlesize': 25})
    
    plt.figure(figsize=(12, 8))

    if seeded_data is not None:
        plt.plot(seeded_data['time_interval'], 
                 seeded_data['to_plot'], 
                 marker='s', linestyle='-', markersize=5, linewidth=2, label='Seeded Average')
    if unseeded_data is not None:
        plt.plot(unseeded_data['time_interval'], 
                 unseeded_data['to_plot'], 
                 marker='s', linestyle='-', markersize=5, linewidth=2, label='Unseeded Average')

    plt.xlabel('Elapsed Seconds')
    plt.ylabel(f'Average {metric}')
    plt.title(f'Average {metric} Over Time ({interval}-second Intervals)')
    plt.legend()
    plt.grid(axis='y', alpha=0.75)
    plt.show()

    last_seeded_value = get_last_metric_value(seeded_data, 'to_plot')
    last_unseeded_value = get_last_metric_value(unseeded_data, 'to_plot')

    return growth_dict, last_seeded_value, last_unseeded_value



# runs_seeded = [3]
# runs_unseeded = []
# percentage_point = 20
# growth = plot_average_and_calculate_growth(sutname="genome-nexus", runs_seeded=runs_seeded, runs_unseeded=runs_unseeded, interval=1, metric='coveredTargets', percentage_point=percentage_point)

# print(growth)
# ========================================= genome-nexus =========================================


# runs_seeded = [1,2,3]
# runs_unseeded = [1,2,3]
# percentage_point = 50
# last_elapsed_second = 3600
# growth, last_seeded_value, last_unseeded_value = plot_average_and_calculate_growth(
#     sutname="catwatch", 
#     runs_seeded=runs_seeded, 
#     runs_unseeded=runs_unseeded, 
#     interval=1, 
#     metric='potentialFaults', 
#     percentage_point=percentage_point, 
#     last_elapsed_second=last_elapsed_second
# )

# print("Growth:", growth)
# print("Last Seeded Value:", last_seeded_value)
# print("Last Unseeded Value:", last_unseeded_value)


# ========================================= scout-api =========================================

# runs_seeded = [1, 2, 3]
# runs_unseeded = [1, 2, 3]
# percentage_point = 50
# growth = plot_average_and_calculate_growth(sutname="scout-api", runs_seeded=runs_seeded, runs_unseeded=runs_unseeded, interval=1, metric='coveredLines' ,devisor='numberOfLines', percentage_point=percentage_point)

# ========================================= catwatch =========================================

runs_seeded = [1,2,3]
runs_unseeded = [1,2,3]
percentage_point = 50
last_elapsed_second = 3600
growth = plot_average_and_calculate_growth(sutname="catwatch", runs_seeded=runs_seeded, runs_unseeded=runs_unseeded, interval=1, metric='covered2xx', percentage_point=percentage_point, last_elapsed_second=last_elapsed_second)

