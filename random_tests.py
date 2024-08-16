import pandas as pd
import matplotlib.pyplot as plt

data = {
    'DOI': ['Paper 1', 'Paper 2', 'Paper 3'],
    '2024-05-15 - 2024-08-15': [100, 60, 40],
}
data1 = {
    'DOI': ['Paper 1', 'Paper 2', 'Paper 3'],
    '2024-02-15 - 2024-05-14': [46, 25, 15],
}
data2 = {
    'DOI': ['Paper 1', 'Paper 2', 'Paper 4'],
    '2023-11-15 - 2024-02-14': [20, 10, 5]
}
df = pd.DataFrame(data)

df['Diff_2024-05-15_2024-08-15_vs_2024-02-15_2024-05-14'] = (df['2024-05-15 - 2024-08-15'] - df['2024-02-15 - 2024-05-14'])/(df['2024-05-15 - 2024-08-15'] - df['2024-02-15 - 2024-05-14'])
df['Diff_2024-02-15_2024-05-14_vs_2023-11-15_2024-02-14'] = (df['2024-02-15 - 2024-05-14'] - df['2023-11-15 - 2024-02-14'])/(df['2024-05-15 - 2024-08-15'] - df['2024-02-15 - 2024-05-14'])

periods = ['2024-05-15 - 2024-08-15', '2024-02-15 - 2024-05-14', '2023-11-15 - 2024-02-14']
diffs = ['Diff_2024-05-15_2024-08-15_vs_2024-02-15_2024-05-14', 'Diff_2024-02-15_2024-05-14_vs_2023-11-15_2024-02-14']

# Flatten the data for plotting
plot_data = []
for i, period in enumerate(periods[:-1]):
    for j, row in df.iterrows():
        plot_data.append({
            'DOI': row['DOI'],
            'Period': period,
            'Citations': row[period],
            'Diff': row[diffs[i]]
        })

plot_df = pd.DataFrame(plot_data)

plt.figure(figsize=(12, 8))

# Assign colors to each paper
colors = {'Paper 1': 'blue', 'Paper 2': 'green', 'Paper 3': 'red'}

for doi in plot_df['DOI'].unique():
    subset = plot_df[plot_df['DOI'] == doi]
    plt.scatter(subset['Period'], subset['Citations'], s=subset['Diff']*100, alpha=0.5, label=doi, color=colors[doi])

plt.xlabel('Time Periods')
plt.ylabel('Number of Citations')
plt.title('Bubble Chart of Citation Differences')
plt.legend()
plt.show()




