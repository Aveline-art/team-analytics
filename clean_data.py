# imports
from csv import DictWriter
import json
import copy

# TODO
# When storing an array, store it properly, because it will be read as a string

# globals
file = 'all_data copy.json'
str_issue_num = 'issue_num'
str_linked_issue = 'linked_issue'
str_opened = 'opened'
str_reopened = 'reopened'
str_closed= 'closed'
str_assigned = 'assigned'
str_pr_made = 'pr_made'
str_labels = 'labels'
pr_fieldnames = [str_issue_num, str_linked_issue, str_opened, str_closed]
issue_fieldnames = [str_issue_num, str_linked_issue, str_opened, str_assigned, str_pr_made, str_closed, str_labels]

def main():
    data = None
    with open(file, 'r') as f:
        data = json.load(f)
    
    reformed_data = add_linked_pr(data)
    convert_to_csv(reformed_data)
    
##################
# Main Functions #
##################

def convert_to_csv(data):
    # moved away, moved into, or deleted issues go into no_data
    no_data = []
    for key, val in data.items():
        try:
            if val['is_pr']:
                dicti = filter_pr(key, val)
                append_to_csv('pr_data.csv', pr_fieldnames, dicti)
            else:
                dicti = filter_issue(key, val)
                append_to_csv('issue_data.csv', issue_fieldnames, dicti)
        except:
            no_data.append(key)
            continue
    create_txt('no_data.txt', no_data)

###########
# Helpers #
###########

def filter_pr(key, val):
    issue_num = key
    linked_issue = val['linked_issue']
    opened = val['timeline'][0][1] if val['timeline'][0][0] == 'opened' else None
    closed = None
    labels = val['labels']
    if len(val['timeline']) == 2:
        if val['timeline'][1][0] == 'closed':
            closed = val['timeline'][1][1]
    dicti = {
        str_issue_num: issue_num,
        str_linked_issue: linked_issue,
        str_opened: opened,
        str_closed: closed,
    }
    return dicti

def filter_issue(key, val):
    dicti = {}
    dicti[str_issue_num] = key
    dicti[str_linked_issue] = val[str_linked_issue]
    perform_func(lambda: get_opened(val['timeline']), dicti, str_opened)
    perform_func(lambda: get_assigned(val['timeline']), dicti, str_assigned)
    perform_func(lambda: get_pr_made(val['timeline']), dicti, str_pr_made)
    perform_func(lambda: get_closed(val['timeline']), dicti, str_closed)
    dicti[str_labels] = '|'.join(val[str_labels])
    return dicti

def append_to_csv(file, fields, data):
    with open(file, 'a', newline='') as f:
        dictwriter_obj = DictWriter(f, fieldnames=fields)
        if f.tell() == 0:
            dictwriter_obj.writeheader()
        dictwriter_obj.writerow(data)

def create_txt(file, data):
    with open(file, 'w') as f:
        f.write(', '.join(data))

def add_linked_pr(data):
    copy_data = copy.deepcopy(data)
    for key, val in data.items():
        try:
            if val['linked_issue']:
                issue_key = val['linked_issue']
                copy_data[issue_key]['linked_issue'] == key
        except:
            continue
    return copy_data

# Helper function that runs a timeline analyzer, and adds the result to a data store if results are found.
def perform_func(func, dicti, key):
    results = func()
    if results:
        dicti[key] = results
    return dicti

# Gets the first opened.
def get_opened(timeline):
    if timeline[0][0] == str_opened:
        return timeline[0][1]
    else:
        return None

# Gets the first assigned.
def get_assigned(timeline):
    for moment in timeline:
        if moment[0] == str_assigned:
            return moment[1]
    return None

# Gets the first pr made.
def get_pr_made(timeline):
    for moment in timeline:
        if moment[0] == str_pr_made:
            return moment[1]
    return None

# Gets the last closed but only if it is after the last open or reopened.
def get_closed(timeline):
    for moment in timeline[::-1]:
        if moment[0] in [str_opened, str_reopened]:
            return None
        elif moment[0] == str_closed:
            return moment[1]
    return None


main()