# Imports
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.dates as mdates

import numpy as np
import pandas as pd
import math

#############    
### Mains ###
#############

def get_x_and_y_from_issue_df(issue_df, col_name_1, col_name_2, label = False):

    new_col_name = f'{col_name_1}_to_{col_name_2}'
    cols_to_extract_dates = ['opened', 'assigned', 'pr_made', 'closed']
    
    # Filter for issues that have an assigned date.
    one_to_two_df = issue_df.loc[issue_df[col_name_1].notna() & issue_df[col_name_2].notna() & filter_df(issue_df['labels'], label), ['issue_num', col_name_1, col_name_2, 'labels']]
    one = one_to_two_df[col_name_1]
    two = one_to_two_df[col_name_2]
    one_to_two_df[new_col_name] = two - one
    
    # Grab x and y values
    df = one_to_two_df
    all_months = extract_all_dates(issue_df, cols_to_extract_dates)
    months = list(dict.fromkeys([f'{item.year}, {item.month}' for item in df.sort_values(by=col_name_2)[col_name_2]]))
    total = df.groupby([df[col_name_2].dt.year, df[col_name_2].dt.month])[new_col_name].sum()
    amount = df.groupby([df[col_name_2].dt.year, df[col_name_2].dt.month])[new_col_name].count()
    monthly_total = total / amount
    times = [t / pd.to_timedelta(1, unit='D') for t in monthly_total]
    
    all_times = []
    for month in all_months:
        try:
            all_times.append(monthly_total[month[0]][month[1]] / pd.to_timedelta(1, unit='D'))
        except:
            all_times.append(0)
    
    all_months = [str(month) for month in all_months]
    
    return all_months, all_times

def get_count_from_issue_df(issue_df, col):
    cols_to_extract_dates = ['opened', 'assigned', 'pr_made', 'closed']
    
    
    all_months = extract_all_dates(issue_df, cols_to_extract_dates)
    total = issue_df.groupby([issue_df[col].dt.year, issue_df[col].dt.month])[col].count()
    
    all_count = []
    for month in all_months:
        try:
            all_count.append(total[month[0]][month[1]])
        except:
            all_count.append(0)
    
    all_months = [str(month) for month in all_months]
    return all_months, all_count

def get_time_from_issue_df(issue_df, col_name_1, col_name_2, label=False):
    one_to_two_df = issue_df.loc[issue_df[col_name_1].notna() & issue_df[col_name_2].notna() & filter_df(issue_df['labels'], label), ['issue_num', col_name_1, col_name_2, 'labels']]
    one = one_to_two_df[col_name_1]
    two = one_to_two_df[col_name_2]
    all_times = two - one
    
    converted_times = [t / pd.to_timedelta(1, unit='D') for t in all_times]
    
    return converted_times

###############    
### Helpers ###
###############

def iqr_outlier_filter(lst):
    q75, q25 = np.percentile(lst, [75 ,25])
    iqr = q75 - q25
    breakpoint = 1.5 * iqr
    new_lst = [num for num in lst if num > q25 - breakpoint and num < q75 + breakpoint]
    
    return new_lst
            
    
def filter_for_labels(lst, label):
    if not label:
        return True

    label = label.lower()
    for item in lst:
        if label in item.lower():
            return True

    return False

def filter_df(col, label):
    result_arr = []
    for item in col:
        result_arr.append(filter_for_labels(item, label))
    return result_arr

def extract_all_dates(issue_df, cols):
    dates = []

    for col in cols:

        years = issue_df[col].dt.year
        months = issue_df[col].dt.month

        for i in range(len(years)):
            if math.isnan(years[i]) or math.isnan(months[i]):
                continue
            pair = (years[i], months[i])
            if pair not in dates:
                dates.append(pair)

    dates.sort(key=lambda x: (x[0], x[1]))
    return dates