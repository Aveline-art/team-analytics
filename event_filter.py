import string_boutique as sb

#################
# Issues Filter #
#################

# Opened
########

# Gets the first opened.
def get_issue_opened(timeline):
    if timeline[0][sb.event_name] == sb.opened:
        return timeline[0][sb.time]
    else:
        return None


# Assigned
##########

# Gets the first assigned by the person who made the PR
def get_issue_assigned(timeline, pr_author_id):
    for moment in timeline:
        if moment[sb.event_name] == sb.assigned and moment[sb.assignee_id] == pr_author_id:
            return moment[sb.time]
    return None

# Pull Request Made
###################

# Gets the first pr made by the assignee.
def get_issue_pr_made(timeline, pr_author_id):
    for moment in timeline:
        if moment[sb.event_name] == sb.pr_made and moment[sb.assignee_id] == pr_author_id:
            return moment[sb.time]
    return None

# Closed
########

# Gets the last closed but only if it is after the last opened or reopened.
def get_issue_closed(timeline):
    for moment in timeline[::-1]:
        if moment[sb.event_name] in [sb.opened, sb.reopened]:
            return None
        elif moment[sb.event_name] == sb.closed:
            return moment[sb.time]
    return None


#######################
# Pull Request Filter #
#######################

# Opened
########

# Gets the first opened.
def get_pr_opened(timeline):
    if timeline[0][sb.event_name] == sb.opened:
        return timeline[0][sb.time]
    else:
        return None


# Reviewed
##########

# Get the time of the first review
def get_pr_reviewed(timeline):
    for moment in timeline:
        if moment[sb.event_name] == sb.reviewed:
            return moment[sb.time]
    return None


# Closed
########

# Get the time when the pr is last closed but only if it is after the last opened or reopened.
def get_pr_closed(timeline):
    for moment in timeline[::-1]:
        if moment[sb.event_name] in [sb.opened, sb.reopened]:
            return None
        elif moment[sb.event_name] == sb.closed:
            return moment[sb.time]
    return None

# Pull request reviews total
############################

def get_pr_num_reviewed(timeline):
    count = 0
    for moment in timeline:
        if moment[sb.event_name] == sb.reviewed:
            count += 1
    return count