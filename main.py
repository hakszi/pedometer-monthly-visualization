import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt
import random
from matplotlib.patches import Rectangle

from matplotlib.colors import ListedColormap


def main():
    # file = 'data.csv'
    # sep = ';'
    # df = read_data(file, sep)    # load the data into the dataframe
    # df = transform_data(df)  # make slight edits (read function for more)

    # alternatively, generate it
    df = generate_data()

    h = []
    add_highlight(h, df['Date'].iloc[0], 'First day of data')
    add_highlight(h, '2024-02-11', 'Some random event')
    add_highlight(h, df['Date'].iloc[-1], "Last day of data")

    df = fill_empty_dates(df)
    y = year_df(df, 2024)

    highlight = [item for item in h if item[0].year == sorted(set(y['Date'].dt.year))[0]]

    # 4x3 visualization plot template
    # lower "figsize" (figure size) and "dpi" to lessen quality and improve performance, speed
    # axes - each given plot (like month in this case)
    fig, axes = plt.subplots(nrows=4,
                             ncols=3,
                             figsize=(20, 20),
                             dpi=500)

    visualize(y, fig, axes, highlight)      # do visualization

def add_highlight(list, date, label):
    return list.append((pd.Timestamp(date), label))

def read_data(file, sep):
    return pd.read_csv(file, sep=sep) # read csv file based on provided separator symbol

def transform_data(df):
    df = df[['End', 'Steps']].rename(columns={'End': 'Date'})   # only take End and Steps column, rename End to Date
    df['Date'] = pd.to_datetime(df['Date']).dt.date             # recognize dates as actual date values

    return df.groupby('Date', as_index=False)['Steps'].sum()    # group and sum Steps based on Step values, so that each Date has only one
                                                                # corresponding value

def generate_data():
    data = np.random.randint(0, 20000, 200)
    start = dt.datetime(2024, 2, 5)
    dates = [start + dt.timedelta(days=i) for i in range(200)]
    df = pd.DataFrame({'Date': dates, 'Steps': data})
    return df.groupby('Date', as_index=False)['Steps'].sum()

def fill_empty_dates(df):
    start = df['Date'].min() - pd.offsets.YearBegin(1)          # the first appearing year's first day
    end = df['Date'].max() + pd.offsets.YearEnd(1)              # the last appearing year's last day
    r = pd.date_range(start, end)                               # dataframe of dates ranging from first day to last day

    return (df.set_index('Date')                                # fill all not existing values with -1 to distinguish from real values
            .reindex(r)                                         # (used so that each year is full 12 months and no empty plot space left)
            .fillna({'Steps': -1})
            .reset_index()
            .rename(columns={'index': 'Date'}))

def year_df(df, year):
    return df[pd.to_datetime(df['Date']).dt.year == year]       # extract given year to a new dataframe
                                                                # (used when choosing year in main() to plot)

def month_df(df, year, month):
    return df[(pd.to_datetime(df['Date']).dt.year == year)          # extract given year's given month to a new dataframe
              & (pd.to_datetime(df['Date']).dt.month == month)]     # (used when splitting a year into months to plot each month)

def df_calendar(date, steps):
    i, j = [], []                                   # week number (i) and week day number (j)
    for d in date:                                  # given dataframe's date
        iso_year, week, weekday = d.isocalendar()   # extract year, week, weekday data from provided date
        if iso_year > d.year:                       # mitigate so that no day will overflow to the next year, useful when there are 53 weeks
            week += 52
        i.append(week)                              # fill week number (i)
        j.append(weekday - 1)                       # fill week day number (j)
    i = np.array(i) - min(i)                        # no idea what this does lmao
    calendar = np.nan * np.zeros((max(i) + 1, 7))   # fill a dataframe with empty values on it's respective size (53x7 or 52x7)
    calendar[i, j] = steps                          # fill the dataframe with real values from Steps' values

    return calendar, i, j                           # this whole function is used so that dates and such can be plotted in labels

def label_days(ax, calendar, i, j, date):
    ni, nj = calendar.shape                                             # grep calendar's row num and column num
    day_of_month = np.nan * np.zeros((ni, nj))                          # fill the dataframe with empty rows and columns
    day_of_month[i, j] = [d.day for d in date]                          # fill the dataframe's rows and columns with real data

    for (i, j), day in np.ndenumerate(day_of_month):                    # print numbering on the daily plots
        if np.isfinite(day):
            ax.text(j, i, int(day), ha='center', va='center', fontsize=12)

    ax.set_xticks(np.arange(nj))                                        # fill day's names
    ax.set_xticklabels(['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], ha='center', fontsize=12)
    ax.xaxis.tick_top()


def label_months(ax, date, i):
    month_labels = np.array(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                             'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    months = np.array([d.month for d in date])                  # store available month names from provided dataframe
    uniq_months = sorted(set(months))                           # store month names uniquely, non-repetitively
    yticks = [np.median(i[months == m]) for m in uniq_months]   # places the month name on the middle of the axis? maybe.
    labels = [month_labels[m - 1] for m in uniq_months]         # no idea
    ax.set(yticks=yticks)
    ax.set_yticklabels(labels, rotation=90, fontsize=12)


def split_year(y):
    min_y = min(sorted(set(y['Date'].dt.month)))        # first day of the given month
    max_y = max(sorted(set(y['Date'].dt.month)))        # last day of the given month
    m = []
    for i in range(min_y, max_y + 1):                   # put each month into a list, later to iterate through and plot one-by-one
        m_tmp = month_df(y, y['Date'].dt.year, i)
        m.append(m_tmp)
    return m                                            # function used to split year into months to plot

def visualize(df, fig, axes, highlight):
    y_split = split_year(df)                            # split given year's dataframe into months
    year = sorted(set(y_split[0]['Date'].dt.year))      # find the year's name (to output in the title)

    fig.subplots_adjust(top=0.95)                                           # reserve space for title
    fig.suptitle(f'Step counts heatmap ({year[0]})', fontsize=35, y=.99)    # print title, and the name of the year dynamically

    fig.subplots_adjust(left=0.15)                      # reserve space on the left side for the calculation table

    max_val = max(df['Steps'].max() for df in y_split)  # maximum Step in the given year to set universal largest low-high range for bar

    plt.rcParams.update({                               # set font that scale better to high DPI (500)
        'font.family': 'DejaVu Sans',
        'text.antialiased': True,
        'font.weight': 'normal'
    })

    # needed to iterate through months
    i = 0

    # iterate through months
    for ax in axes.flat:

        # while i is smaller than the existing months (since we filled it, it's 12, but still, better this way)
        if i < len(y_split):
            calendar, week_num, day_num = df_calendar(y_split[i]['Date'], y_split[i]['Steps'])  # extract date layout pre-filled (df_calendar) with data, week numbers, day numbers
            label_days(ax, calendar, week_num, day_num, y_split[i]['Date'])                     # get the name of the 7 days of the week for the given week
            label_months(ax, y_split[i]['Date'], week_num)                                      # get the month's name

            cmap = plt.get_cmap('summer').copy()                                                # create a custom color map
            cmap.set_under('lightgray')                                                         # mark under vmin values as lightgray, aka invalid (thus setting not existing dates as -1 in value)
            im = ax.imshow(calendar, interpolation='none', cmap=cmap, vmin=0, vmax=max_val)     # set color map, min value, max value; no idea what is interpolation in this case (also note the set global maximum)

            cbar = fig.colorbar(im, ax=ax, shrink=0.8)                                          # set the color bar, shrink so looks more compact
            cbar.ax.tick_params(labelsize=12)                                                   # color bar labels to be bit bigger

            tick_values = cbar.get_ticks()                                                      # get the ticks for the table
            table_data = [[f"{int(v)}", f"{v * 0.0007:.1f} km"] for v in tick_values]           # prepare table values
            table_ax = fig.add_axes([.05, .1, .05, .8])                                         # set table location
            table_ax.axis('off')                                                                # no idea what this does
            conversion_table = table_ax.table(                                                  # create the table
                cellText=table_data,
                colLabels=('Steps', 'km'),
                loc='center',
                cellLoc='left')
            conversion_table.auto_set_font_size(False)                                          # no automatic font size
            conversion_table.set_fontsize(12)                                                   # set font size to be bit bigger
            conversion_table.scale(1.7, 1.7)                                                    # set scale

            if highlight:
                for target_date, note in highlight:
                    if (y_split[i]['Date'] == target_date).any():
                        iso_year, target_week, target_weekday = target_date.isocalendar()
                        current_weeks = [d.isocalendar()[1] for d in y_split[i]['Date']]
                        min_week = min(current_weeks)
                        row = target_week - min_week
                        col = target_weekday - 1
                        rect = Rectangle(
                            (col - 0.5, row - 0.5),
                            1, 1,
                            edgecolor='red',
                            facecolor='none',
                            linewidth=1.5
                        )
                        ax.add_patch(rect)

                fig.subplots_adjust(left=.15, right=0.80)
                highlight_patches = [
                    Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='none', linewidth=2)
                    for _ in highlight
                ]
                fig.legend(
                    handles=highlight_patches,
                    labels=[f"{d.strftime('%Y-%m-%d')}: {n}" for d, n in highlight],
                    loc='center right',
                    bbox_to_anchor=(.95, 0.5),
                    fontsize=10,
                    title='Highlighted dates',
                    title_fontsize='12'
                )


            i += 1                                                                              # don't forget to iterate the if statement

    plt.savefig('output.png', dpi=500)                                                    # save the heatmap as pdf for best quality
    # plt.show()                                                                                # or just show it, how neat is that

main()