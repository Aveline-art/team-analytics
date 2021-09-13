# Default Library imporats
from csv import DictWriter
import json
import sys

# Imports from this project
import string_boutique as sb
import event_filter as ef

# test issue: 1671
# test pr: 1837

# globals
data = None


def main(file, outfile_issue='issue_data.csv', outfile_pr='pr_data.csv', outfile_no='no_data.txt'):
    with open(file, 'r') as f:
        data = json.load(f)

    csv_filter = Filter(data)
    csv_filter.start_filter(outfile_issue, outfile_pr, outfile_no)


class Filter():
    def __init__(self, data) -> None:
        self.data = data
        self.issue_data = []
        self.outfile_issue = None
        self.pr_data = []
        self.outfile_pr = None
        self.no_data = []
        self.outfile_no = None
        pass

    def set_outfile_issue(self, name):
        self.outfile_issue = name
    
    def set_outfile_pr(self, name):
        self.outfile_pr = name
    
    def set_outfile_no(self, name):
        self.outfile_no = name

    def start_filter(self, outfile_issue='issue_data.csv', outfile_pr='pr_data.csv', outfile_no='no_data.txt'):
        self.set_outfile_issue(outfile_issue)
        self.set_outfile_pr(outfile_pr)
        self.set_outfile_no(outfile_no)

        for key, val in self.data.items():
            try:
                if val[sb.is_pr]:
                    dicti = self.filter_pr(key, val)
                    self.pr_data.append(dicti)
                else:
                    dicti = self.filter_issue(key, val)
                    self.issue_data.append(dicti)
            except:
                self.no_data.append(key)
                continue
            
        write_to_csv(self.outfile_issue, self.issue_data)
        write_to_csv(self.outfile_pr, self.pr_data)
        create_txt(self.outfile_no, self.no_data)
    
    def filter_issue(self, key, val):
        dicti = {}
        dicti[sb.issue_num] = key
        dicti[sb.linked_issue] = val[sb.linked_issue]
        dicti[sb.opened] = ef.get_issue_opened(val[sb.timeline])
        if val[sb.linked_issue]:
            pr_author_id = self.data[str(val[sb.linked_issue])][sb.creator_id]
            dicti[sb.assigned] = ef.get_issue_assigned(val[sb.timeline], pr_author_id)
            dicti[sb.pr_made] = ef.get_issue_pr_made(val[sb.timeline], pr_author_id)
        else:
            dicti[sb.assigned] = None
            dicti[sb.pr_made] = None
        dicti[sb.closed] = ef.get_issue_closed(val[sb.timeline])
        dicti[sb.labels] = sb.join_delimiter.join(val[sb.labels])

        return dicti
    
    def filter_pr(self, key, val):
        dicti = {}
        dicti[sb.issue_num] = key
        dicti[sb.linked_issue] = val[sb.linked_issue]
        dicti[sb.opened] = ef.get_pr_opened(val[sb.timeline])
        dicti[sb.review_count] = ef.get_pr_reviewed(val[sb.timeline])
        dicti[sb.closed] = ef.get_pr_closed(val[sb.timeline])
        dicti[sb.review_count] = ef.get_pr_num_reviewed(val[sb.timeline])
        dicti[sb.labels] = sb.join_delimiter.join(val[sb.labels])

        return dicti


##################
# Main Functions #
##################


def write_to_csv(file, lst):
    with open(file, 'w', newline='') as f:
        dictwriter_obj = DictWriter(f, fieldnames=lst[0].keys())
        dictwriter_obj.writeheader()
        for item in lst:
            dictwriter_obj.writerow(item)


###########
# Helpers #
###########

# Helper function that runs a timeline analyzer, and adds the result to a data store if results are found.
def perform_func(func, dicti, key):
    results = func()
    dicti[key] = results
    return dicti


def create_txt(file, lst):
    with open(file, 'w') as f:
        f.write(', '.join(lst))


###############
# main() call #
###############

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    main(*sys.argv[1:])