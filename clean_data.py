# imports
from csv import DictWriter
import json
import string_boutique as sb

# test issue: 1671
# test pr: 1837

# globals
file = 'all_data.json'
data = None
with open(file, 'r') as f:
    data = json.load(f)


def main():
    # Moved away, moved into, or deleted issues goes into no_data
    no_data = []
    for key, val in data.items():
        try:
            if val[sb.is_pr]:
                dicti = filter_pr(key, val)
                append_to_csv('pr_data.csv', dicti)
            else:
                dicti = filter_issue(key, val)
                append_to_csv('issue_data.csv', dicti)
        except:
            no_data.append(key)
            continue
    create_txt('no_data.txt', no_data)
    
##################
# Main Functions #
##################


def filter_issue(key, val):
    dicti = {}
    dicti[sb.issue_num] = key
    dicti[sb.linked_issue] = val[sb.linked_issue]
    perform_func(lambda: get_issue_opened(val[sb.timeline]), dicti, sb.opened)
    if val[sb.linked_issue]:
        perform_func(lambda: get_issue_assigned(val[sb.timeline], str(val[sb.linked_issue])), dicti, sb.assigned)
        perform_func(lambda: get_issue_pr_made(val[sb.timeline], str(val[sb.linked_issue])), dicti, sb.pr_made)
    else:
        dicti[sb.assigned] = None
        dicti[sb.pr_made] = None
    perform_func(lambda: get_issue_closed(val[sb.timeline]), dicti, sb.closed)
    dicti[sb.labels] = sb.join_delimiter.join(val[sb.labels])

    return dicti


def filter_pr(key, val):
    dicti = {}
    dicti[sb.issue_num] = key
    dicti[sb.linked_issue] = val[sb.linked_issue]
    perform_func(lambda: get_pr_opened(val[sb.timeline]), dicti, sb.opened)
    perform_func(lambda: get_pr_reviewed(val[sb.timeline]), dicti, sb.reviewed)
    perform_func(lambda: get_pr_closed(val[sb.timeline]), dicti, sb.closed)
    perform_func(lambda: get_pr_num_reviewed(val[sb.timeline]), dicti, sb.review_count)
    dicti[sb.labels] = sb.join_delimiter.join(val[sb.labels])

    return dicti


def append_to_csv(file, data):
    with open(file, 'a', newline='') as f:
        dictwriter_obj = DictWriter(f, fieldnames=data.keys())
        if f.tell() == 0:
            dictwriter_obj.writeheader()
        dictwriter_obj.writerow(data)


###########
# Helpers #
###########

def create_txt(file, data):
    with open(file, 'w') as f:
        f.write(', '.join(data))


# Helper function that runs a timeline analyzer, and adds the result to a data store if results are found.
def perform_func(func, dicti, key):
    results = func()
    dicti[key] = results
    return dicti


# Gets the first opened.
def get_issue_opened(timeline):
    if timeline[0][sb.event_name] == sb.opened:
        return timeline[0][sb.time]
    else:
        return None


# Gets the first assigned by the person who made the PR
def get_issue_assigned(timeline, linked_issue):
    for moment in timeline:
        if moment[sb.event_name] == sb.assigned and moment[sb.assignee_id] == data[linked_issue][sb.creator_id]:
            return moment[sb.time]
    return None


# Gets the first pr made by the assignee.
def get_issue_pr_made(timeline, linked_issue):
    for moment in timeline:
        if moment[sb.event_name] == sb.pr_made and moment[sb.assignee_id] == data[linked_issue][sb.creator_id]:
            return moment[sb.time]
    return None


# Gets the last closed but only if it is after the last opened or reopened.
def get_issue_closed(timeline):
    for moment in timeline[::-1]:
        if moment[sb.event_name] in [sb.opened, sb.reopened]:
            return None
        elif moment[sb.event_name] == sb.closed:
            return moment[sb.time]
    return None


# Gets the first opened.
def get_pr_opened(timeline):
    if timeline[0][sb.event_name] == sb.opened:
        return timeline[0][sb.time]
    else:
        return None


# Get the time of the first review
def get_pr_reviewed(timeline):
    for moment in timeline:
        if moment[sb.event_name] == sb.reviewed:
            return moment[sb.time]
    return None


# Get the time when the pr is last closed but only if it is after the last opened or reopened.
def get_pr_closed(timeline):
    for moment in timeline[::-1]:
        if moment[sb.event_name] in [sb.opened, sb.reopened]:
            return None
        elif moment[sb.event_name] == sb.closed:
            return moment[sb.time]
    return None


def get_pr_num_reviewed(timeline):
    count = 0
    for moment in timeline:
        if moment[sb.event_name] == sb.reviewed:
            count += 1
    return count
    


###############
# main() call #
###############

main()