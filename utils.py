# Imports
import numpy as np
import pandas as pd
import string_boutique as sb

#############
### Mains ###
#############

def get_time_diff_from_issue_df(df: pd.DataFrame, col_name_1: str, col_name_2: str, in_labels: list=[], out_labels: list=[]) -> tuple:
    """ Takes a dataframe and extracts average time different between columns per month

    Arguments:
        df {pd.DataFrame} -- a dataframe that assumes that the below variables denotes columns with pd.TimeStamp or NaN datatype
        col_name_1 {str} -- string that denotes a column's name, acts as the subtrahend when compared
        col_name_2 {str} -- string that denotes a column's name, acts as the minuend when compared

    Keyword Arguments:
        in_labels {list[str]} -- a list of labels to verify is in df. Default is an empty list
        out_labels {list[str]} -- a list of labels to verify is not in df. Default is an empty list
    
    Returns:
        {tuple(x, y)} --
            x {list[str]} -- a list of strings containing the year and month in order
            y {list[float]} -- a list of floats representing average difference (in days) between two columns per year per month
    """

    # Create a copy to avoid modifying the original
    copy_df = df.copy()

    # Get all the months which will be returned as x values.
    all_months = extract_months(copy_df)

    # Clean columns.
    cleaned_df = copy_df.dropna(subset=[col_name_1, col_name_2])
    cleaned_df = cleaned_df[cleaned_df[sb.labels].apply(lambda x: filter_by_labels(x, in_labels, out_labels))]
    
    # Create new column that consists of the time difference between one column and another.
    one = cleaned_df[col_name_1]
    two = cleaned_df[col_name_2]
    new_col_name = f'{col_name_1}_to_{col_name_2}'
    cleaned_df[new_col_name] = two - one
    
    # Compute the average time difference per year, per month.
    total = cleaned_df.groupby([cleaned_df[col_name_2].dt.year, cleaned_df[col_name_2].dt.month])[new_col_name].sum()
    amount = cleaned_df.groupby([cleaned_df[col_name_2].dt.year, cleaned_df[col_name_2].dt.month])[new_col_name].count()
    monthly_total = total / amount
    
    # Format data to fill in empty data, and correct the datatypes.
    complete_monthly_total = []
    for month in all_months:
        try:
            complete_monthly_total.append(monthly_total[month[0]][month[1]] / pd.to_timedelta(1, unit='D'))
        except:
            complete_monthly_total.append(0)
    all_months = [str(month) for month in all_months]
    
    return all_months, complete_monthly_total


def get_count_from_issue_df(df: pd.DataFrame, col: str, in_labels: list=[], out_labels: list=[]) -> tuple:
    """ Takes a dataframe and counts the number of results for a specified column per year per month.

    Arguments:
        df {pd.DataFrame} -- a dataframe that assumes that the below variables denotes columns with pd.TimeStamp or NaN datatype
        col {str} -- string that denotes a column's name

    Keyword Arguments:
        in_labels {list[str]} -- a list of labels to verify is in df. Default is an empty list
        out_labels {list[str]} -- a list of labels to verify is not in df. Default is an empty list
    
    Returns:
        {tuple(x, y)} --
            x {list[str]} -- a list of strings containing the year and month in order
            y {list[int]} -- a list of int representing the count of issues per month
    """

    # Create a copy to avoid modifying the original
    copy_df = df.copy()

    # Get all the months which will be returned as x values.
    all_months = extract_months(copy_df)

    # Clean columns.
    cleaned_df = copy_df.dropna(subset=[col])
    cleaned_df = cleaned_df[cleaned_df[sb.labels].apply(lambda x: filter_by_labels(x, in_labels, out_labels))]

    # Format data to account for empty months and datatypes.
    total = cleaned_df.groupby([cleaned_df[col].dt.year, cleaned_df[col].dt.month])[col].count()
    all_count = []
    for month in all_months:
        try:
            all_count.append(total[month[0]][month[1]])
        except:
            all_count.append(0)
    all_months = [str(month) for month in all_months]

    return all_months, all_count


def get_time_from_issue_df(df, col_name_1, col_name_2, in_labels=[], out_labels=[]) -> list:
    """ Takes a dataframe and returns a list of time differences between one column and another.

    Arguments:
        df {pd.DataFrame} -- a dataframe that assumes that the below variables denotes columns with pd.TimeStamp or NaN datatype
        col_name_1 {str} -- string that denotes a column's name, acts as the subtrahend when compared
        col_name_2 {str} -- string that denotes a column's name, acts as the minuend when compared

    Keyword Arguments:
        in_labels {list[str]} -- a list of labels to verify is in df. Default is an empty list
        out_labels {list[str]} -- a list of labels to verify is not in df. Default is an empty list
    
    Returns:
        {list[float]} -- a list of floats representing the time difference between two columns
    """

    # Create a copy to avoid modifying the original
    copy_df = df.copy()

    # Clean columns.
    cleaned_df = copy_df.dropna(subset=[col_name_1, col_name_2])
    cleaned_df = cleaned_df[cleaned_df[sb.labels].apply(lambda x: filter_by_labels(x, in_labels, out_labels))]

    # Find time difference between two columns per row.
    one = cleaned_df[col_name_1]
    two = cleaned_df[col_name_2]
    all_times = two - one
    
    # Format times into floats.
    converted_times = [t / pd.to_timedelta(1, unit='D') for t in all_times]
    
    return converted_times

###############    
### Helpers ###
###############

# Takes a list and removes all values that does not meet the iqr outlier standard. Preserves list order.
def iqr_outlier_filter(lst):
    q75, q25 = np.percentile(lst, [75 ,25])
    iqr = q75 - q25
    breakpoint = 1.5 * iqr
    new_lst = [num for num in lst if num > q25 - breakpoint and num < q75 + breakpoint]
    
    return new_lst


def filter_by_labels(lst: list, in_labels: list=[], out_labels: list=[]) -> bool:
    """ Takes the list from the labels column and check cross reference with a custom in_labels and out_labels list. Returns True if the in_labels are in and out_labels are out. False otherwise.

    Arguments:
        lst {list[str]} -- a list of labels from the labels column

    Default Arguments:
        in_labels {list[str]} -- a list of labels to verify is in lst. Default is an empty list.
        out_labels {list[str]} -- a list of labels to verify is not in lst. Default is an empty list.
    
    Returns:
        {bool} -- True if the out_labels are out, and in_labels are in. False otherwise.
    """
    # Turn a string into a list to support adding strings.
    if not isinstance(in_labels, list): in_labels = [in_labels]
    if not isinstance(out_labels, list): out_labels = [out_labels]
    
    # Lowers all words for string matching.
    lst = [s.lower() for s in lst]
    in_labels = [s.lower() for s in in_labels]
    out_labels = [s.lower() for s in out_labels]
    
    # Return False if an out_label is found in any label.
    if out_labels:
        for label in out_labels:
            for word in lst:
                if label in word:
                    return False
    
    # Returns False if an in_label is not found in any label.
    for label in in_labels:
        if not any([label in s for s in lst]):
            return False
    
    # Returns True since all checks had passed.
    return True

def extract_months(df: pd.DataFrame) -> list:
    """ Takes a dataframe and examine all columns for pd.Timestamp datatype, and extracts year/month information.

    Arguments:
        df {pd.DataFrame} -- a dataframe

    Returns:
        {ist[tuple]} -- A list of tuples sorted by year, then month.
    """

    dates = []
    for col_name in df:
        column = df[col_name]
        for val in column:
            if isinstance(val, pd.Timestamp):
                pair = (val.year, val.month)
                if pair not in dates:
                    dates.append(pair)
    dates.sort(key=lambda x: (x[0], x[1]))
    return dates


# A function used to filter out certain parts of a data frame before running it through a custom function. Debug use only.
def examine_data(df: pd.DataFrame, col_name_1: str, col_name_2: str, in_labels: list=[], out_labels: list=[], rows: int=10, func=lambda x, y: x):
    # Create a copy to avoid modifying the original
    copy_df = df.copy()

    # Clean columns.
    cleaned_df = copy_df.dropna(subset=[col_name_1, col_name_2])
    cleaned_df = cleaned_df[cleaned_df[sb.labels].apply(lambda x: filter_by_labels(x, in_labels, out_labels))]
    pd.set_option("display.max_rows", rows)
    return func(cleaned_df, rows)