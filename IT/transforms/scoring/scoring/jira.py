import os
import sys
import json
import pandas as pd
from dateutil import parser as date_parser 

# Firefighter
# Collaborative
# Skilled
# Takes Ownership 
# Responsive 

def annotate_issue(issue):

    # How much discussion was there. 
    historylen = sum(issue['discussants'].values())
    issue['discussionlen'] = historylen

    # Whether more than two people collaborated (two being typical)
    # opener and closer
    issue['groupsize'] = len(issue['discussants'])
    
    issue['firefight'] = 1 if issue['issuetype'] in ['Emergency', 'Epic'] else 0
    issue['stability'] = 1 if issue['issuetype'] in ['Bug', 'Regular', 'Internal Task'] else 0
    issue['skilled'] = 1 if issue['issuetype'] in ['Design'] else 0
    

def gather_project_issues(project):

    name = project['name']

    summary = {
        'issues': [],
        'people': []        
    }

    for issue in project['issues']:

        history = issue['history'] 

        issue_summary = {
            'project': name,
            'components': issue['components'], 
            'issueid': issue['externalId'],
            'issuetype': issue['issueType'],
            'status': issue['status'],
            'resolution': issue.get('resolution',None),
            'priority': issue['priority'],
            'assignee': issue.get('assignee',None),
            'reporter': issue['reporter'],
            'watchers': issue['watchers'],
        }

        # Process the people involved.        
        discussants = [h['author'] for h in history]
        discussants = { d: discussants.count(d) \
                        for d in list(set(discussants))} 
        issue_summary['discussants'] = discussants

        people = [issue['reporter']] + issue['watchers'] + \
                 list(discussants.keys())
        issue_summary['people'] = people

        # Now insert the response time
        responses = {} 
        for i in range(len(history)):
            if i == 0: # ignore the first.
                continue
            curr = history[i]
            prev = history[i-1]
            author = curr['author'] 

            # See how the person to responds to posts from others..
            if curr['author'] == prev['author']:
                continue

            prev_dt = date_parser.parse(prev['created'])
            curr_dt = date_parser.parse(curr['created'])
            diff = (curr_dt - prev_dt)
            diff = diff.days + diff.seconds/86400.0
            if author not in responses: 
                responses[author] = [diff, 1]
            else:
                responses[author][0] += diff
                responses[author][1] += 1

        responses = { k: round(v[0]/v[1],2) for k,v in responses.items()}
        issue_summary['responses'] = responses
        
        annotate_issue(issue_summary)
        
        summary['people'].extend(people) 
        summary['issues'].append(issue_summary)

    # Cleanup 
    summary['issues'] = pd.DataFrame(summary['issues'])
    summary['people'] = list(set(summary['people']))
    
    return summary

def gather_issues(rawdata):

    print(list(rawdata.keys()))

    rawdata['projects']
    
    results = [] 
    for project in rawdata['projects']:
        result = gather_project_issues(project)
        results.append(result)

    issuedf = pd.concat([r['issues'] for r in results])

    # Flatten people
    people = []
    for r in results:
        people.extend(r['people'])
    people = list(set(people))

    return issuedf, people

def generate_project_summary(issuedf):

    def summarize(rows):
        issues = rows['issueid'].nunique()
        firefights = int(rows['firefight'].sum())

        groupsize = round(rows['groupsize'].mean(),1)
        threeplus = rows[rows['groupsize'] > 2].shape[0] 
        
        return pd.Series({
            'issues': issues,
            'firefight_percent': round(100*firefights/issues,1),
            'group_size': groupsize,
            'threeplus_group_percent': round(100*threeplus/issues,1),
        })

    projectdf = issuedf.groupby('project').apply(summarize)
    projectdf = projectdf.reset_index()

    threshold1 = projectdf['issues'].quantile(0.8)
    threshold2 = projectdf['issues'].quantile(0.2)

    def compute_complexity(count):
        if count <= threshold2:
            return 'low'
        elif count >= threshold1:
            return 'high'
        else:
            return 'normal' 
    projectdf.loc[:, 'complexity'] = projectdf['issues'].apply(compute_complexity)

    threshold1 = projectdf['firefight_percent'].quantile(0.8)
    threshold2 = projectdf['firefight_percent'].quantile(0.2)    

    def compute_criticality(percent):
        if percent <= threshold2:
            return 'low'
        elif percent >= threshold1:
            return 'high'
        else:
            return 'normal'     
    projectdf.loc[:, 'criticality'] = projectdf['firefight_percent'].apply(compute_criticality)
  
    threshold1 = projectdf['threeplus_group_percent'].quantile(0.7)
    def compute_collaboration(percent):
        if percent > threshold1:
            return 'high'
        else:
            return 'normal' 
        
    projectdf.loc[:, 'collaboration_level'] = projectdf['threeplus_group_percent'].apply(compute_collaboration)    

    
    return projectdf 

def generate_person_summary(df, p):
    """
    """

    # Which rows are relevant
    df = df[df['people'].apply(lambda l: p in l)]

    # Total issues 
    issues = df.shape[0] 

    firefights = df['firefight'].sum()

    ownership = df[df['assignee'] == p].shape[0]

    successful = df[(df['assignee'] == p) &
                    (df['resolution'].isin(['Fixed', 'Resolved']))].shape[0]

    groupsize = df['groupsize'].mean().round(1)
    threeplus = df[df['groupsize'] > 2].shape[0]

    
    # Firefighter
    # Collaborative
    # Skilled 
    # Takes Ownership 
    # Responsive
    return {
        'person': p,
        'issues': issues,
        'avg_groupsize': groupsize, 
        'threeplus_percent': round(100*threeplus/issues,1), 
        'firefight_percent': round(100*firefights/issues,1),
        'ownership_percent': round(100*ownership/issues,1),
        'success_percent': round(100*successful/issues,1),
        'delivery_percent': round(100*successful/ownership,1),
    }
    
    
def generate_people_summary(issuedf, projectdf):

    df = pd.merge(issuedf, projectdf,
             how='inner',
             left_on = 'project',
             right_on = 'project')

    # Gather unique people 
    peoples = list(df['people'].values)
    people = list(set([p for subset in peoples for p in subset]))
    
    results = [] 
    for p in people: 
        result = generate_person_summary(df, p) 
        results.append(result)

    df = pd.DataFrame(results)
    return df

def compute(filename):

    # Load rawdata 
    rawdata = json.load(open(filename))

    # Gather issues 
    issuedf, people = gather_issues(rawdata)

    projectdf = generate_project_summary(issuedf) 

    peopledf = generate_people_summary(issuedf, projectdf) 

    print(peopledf)
    
    return {
        'issues': issuedf,
        'project': projectdf,
        'people': peopledf
    }
