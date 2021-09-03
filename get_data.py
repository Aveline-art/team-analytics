# imports
import json
import pprint as pp
import re
import requests

# globals
owner = 'hackforla'
repo = 'website'
with open('authorization.txt', 'r') as f:
    authorization = f.read() 
headers = {
    'Accept': 'application/vnd.github.mockingbird-preview+json',
    'Authorization': f'Bearer {authorization}',
}

start_num = 1
end_num = 2216

# cross-referenced events are a special case, so they are ignored, linked pr found by reading the pr body
# opened is not in timeline, must find through issue api
events_of_interest = ['assigned', 'closed', 'reopened']
pr_events_of_interest = ['closed', 'reopened']

def main():
    data = {}
    for issue_num in range(start_num, end_num + 1):
        print(f'collecting issue #{issue_num}...', end='')

        try:
            issue = get_issue(issue_num)
            timeline = get_timeline(issue_num)
            print('timeline len: ', len(timeline))
            is_pr = 'pull_request' in issue
            brief_timeline = filter_timeline(issue, timeline, is_pr)
            data[issue_num] = {
                'timeline': brief_timeline,
                'title': issue['title'],
                'is_pr': is_pr,
                'linked_issue': find_linked_issue(issue['body']) if is_pr else None,
                'labels': None if is_pr else [label['name'] for label in issue['labels']],
            }
        except:
            print(f'An exception occued with issue #{issue_num}')
            data[issue_num] = {
                'message': 'Not Found!'
            }
            continue

        if issue_num % 10 == 0:
            append_json('all_data copy', data)
            data = {}
    
    append_json('all_data copy', data)
    

##################
# Main Functions #
##################

def get_timeline(issue_num):

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

def filter_timeline(issue, timeline, is_pr):
    if is_pr: 
        event_types = pr_events_of_interest
    else:
        event_types = events_of_interest

    brief_timeline = [['opened', issue['created_at']]]

    for event in timeline:
        if is_linked(issue['number'], event):
            brief_event = ['pr_made', event['created_at']]
            brief_timeline.append(brief_event)
        
        if event['event'] in event_types:
            brief_event = [event['event'], event['created_at']]
            brief_timeline.append(brief_event)
    
    return brief_timeline

###########
# Helpers #
###########

def is_linked(issue_num, event):
    if event['event'] == 'cross-referenced':
        body = event['source']['issue']['body']
        if find_linked_issue(body) == str(issue_num):
            return True
    
    return False


def get_issue(issue_num):
    issue_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}'
    request = requests.get(url=issue_url, headers=headers)
    return request.json()


def find_linked_issue(text):
    KEYWORDS = ['close', 'closes', 'closed', 'fix', 'fixes', 'fixed', 'resolve', 'resolves', 'resolved']
    re_array = []
    for word in KEYWORDS:
        re_array.append(f"[\\n|\\s|^]{word} #\\d*\\s|^{word} #\\d*\\s|\\s{word} #\\d*$|^{word} #\\d*$")

    re_string = r'|'.join(re_array)
    regex = re.compile(re_string, re.IGNORECASE)
    matches = regex.findall(text)

    if len(matches) == 1:
        issueNumber = re.findall(r'\d+', matches[0])
        return issueNumber[0]
    else:
        return None


def write_json(name, data):
    with open(f'{name}.json', 'w') as f:
        f.write(json.dumps(data))


def append_json(name, data):
    print('downloading...', end='')
    named_json = {}
    with open(f'{name}.json', 'r') as f:
        try:
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