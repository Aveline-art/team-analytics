# imports
import json
import pprint as pp
import re
import requests
import string_boutique as sb

# globals
owner = 'hackforla'
repo = 'website'
with open('authorization.txt', 'r') as f:
    authorization = f.read() 
headers = {
    'Accept': 'application/vnd.github.mockingbird-preview+json',
    'Authorization': f'Bearer {authorization}',
}
start_num = 1671
end_num = 1837
outfile = 'hahah'

# test issue: 1671
# test pr: 1837

def main():
    # For cacheing data.
    data = {}
    for issue_num in range(start_num, end_num + 1):
        print(f'collecting issue #{issue_num}...')
        try:
            # Get data from the relevant APIs
            issue = get_issue_API(issue_num)
            timeline = get_timeline_API(issue_num)
            
            # Create an object that is added to our data
            if 'pull_request' in issue:
                data_obj = comb_pr(issue, timeline)
            else:
                data_obj = comb_issue(issue, timeline, issue_num)

            # Adds object to data
            data[str(issue_num)] = data_obj
        except:
            # Creates an alternate object if data cannot be found for whatever reason.
            print(f'An exception occued with issue #{issue_num}')
            data[str(issue_num)] = {
                sb.message: 'Not Found!'
            }
            continue

        # Saves every 10th issue we have read
        if issue_num % 10 == 0:
            append_json(outfile, data)
            data = {}
    
    # Saves one last time.
    append_json(outfile, data)
    

##################
# Main Functions #
##################

def get_issue_API(issue_num):
    issue_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}'
    request = requests.get(url=issue_url, headers=headers)
    return request.json()


def get_timeline_API(issue_num):
    def helper(issue_num, num=1, store=[], depth_limit=10):
        timeline_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/timeline'
        request = requests.get(url=timeline_url, params={
            'page': num,
            'per_page': 100
        }, headers=headers)
        result = request.json()
        store.extend(result)
        if not result or num == depth_limit:
            return store
        return helper(issue_num, num + 1, store)
    return helper(issue_num)


def comb_issue(issue, timeline, issue_num):
    # Create title
    title = issue['title']

    # Create is_pr
    is_pr = False

    # Create creator_id
    creator_id = issue['user']['id']

    # Create brief_timeline and linked_issue
    linked_issue = None
    brief_timeline = [{
        sb.event_name: sb.opened,
        sb.time: issue['created_at'],
    }]
    for event in timeline:
        event_type = event['event']
        if event_type == 'assigned':
            brief_event = {
                sb.event_name: sb.assigned,
                sb.assignee_id: event['assignee']['id'],
                sb.time: event['created_at'],
            }
            brief_timeline.append(brief_event)
        
        elif event_type == 'closed':
            brief_event = {
                sb.event_name: sb.closed,
                sb.time: event['created_at'],
            }
            brief_timeline.append(brief_event)
        
        elif event_type == 'reopened':
            brief_event = {
                sb.event_name: sb.opened,
                sb.time: event['created_at'],
            }
            brief_timeline.append(brief_event)
        
        elif event_type == 'cross-referenced':
            if str(issue_num) == find_linked_issue(event['source']['issue']['body']):
                linked_issue = event['source']['issue']['number']
                brief_event = {
                    sb.event_name: sb.pr_made,
                    # TODO
                    sb.assignee_id: event['source']['issue']['user']['id'],
                    sb.time: event['created_at'],
                }
                brief_timeline.append(brief_event)
    
    # Create labels
    labels = [label['name'] for label in issue['labels']]

    # Record created variables in data_obj
    data_obj = {
        sb.title: title,
        sb.is_pr: is_pr,
        sb.creator_id: creator_id,
        sb.linked_issue: linked_issue,
        sb.timeline: brief_timeline,
        sb.labels: labels,
    }

    return data_obj


def comb_pr(issue, timeline):
    # Create title
    title = issue['title']

    # Create is_pr
    is_pr = True

    # Create creator_id
    creator_id = issue['user']['id']

    # Create linked_issue
    linked_issue = find_linked_issue(issue['body'])

    # Create brief_timeline and linked_issue
    brief_timeline = [{
        sb.event_name: sb.opened,
        sb.time: issue['created_at'],
    }]
    for event in timeline:
        event_type = event['event']
        if event_type == 'reviewed':
            brief_event = {
                sb.event_name: sb.reviewed,
                sb.state: event['state'],
                sb.time: event['submitted_at'],
            }
            brief_timeline.append(brief_event)
        
        elif event_type == 'closed':
            brief_event = {
                sb.event_name: sb.closed,
                sb.time: event['created_at'],
            }
            brief_timeline.append(brief_event)
        
        elif event_type == 'merged':
            brief_event = {
                sb.event_name: sb.merged,
                sb.time: event['created_at']
            }
            brief_timeline.append(brief_event)
        
        elif event_type == 'committed':
            brief_event = {
                sb.event_name: sb.comitted,
                sb.time: event['committer']['date'],
            }
            brief_timeline.append(brief_event)
    
    # Create labels
    labels = [label['name'] for label in issue['labels']]

    # Record created variables in data_obj
    data_obj = {
        sb.title: title,
        sb.is_pr: is_pr,
        sb.creator_id: creator_id,
        sb.linked_issue: linked_issue,
        sb.timeline: brief_timeline,
        sb.labels: labels,
    }

    return data_obj


###########
# Helpers #
###########

def find_linked_issue(text):
    KEYWORDS = ['close', 'closes', 'closed', 'fix', 'fixes', 'fixed', 'resolve', 'resolves', 'resolved']
    re_array = []
    for word in KEYWORDS:
        re_array.append(f"[\\n|\\s|^]{word} #\\d+\\s|^{word} #\\d+\\s|\\s{word} #\\d+$|^{word} #\\d+$")

    re_string = r'|'.join(re_array)
    regex = re.compile(re_string, re.IGNORECASE)
    matches = regex.findall(text)

    if len(matches) == 1:
        issueNumber = re.findall(r'\d+', matches[0])
        return issueNumber[0]
    else:
        return None


def append_json(name, data):
    print('downloading...', end='')
    named_json = {}

    try:
        with open(f'{name}.json', 'r') as f:
            named_json = json.loads(f.read())
    except:
        pass

    with open(f'{name}.json', 'w') as f:
        named_json.update(data)
        f.write(json.dumps(named_json))

    print('done')
    

###############
# main() call #
###############

main()