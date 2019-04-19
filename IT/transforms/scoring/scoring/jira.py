import os
import sys
import json
import pandas as pd
from collections import OrderedDict 
from dateutil import parser as date_parser 

# Firefighter
# Collaborative
# Skilled
# Takes Ownership 
# Responsive 

def get_documentation():
    return {
        'member': "Team Member",
        'project': "Name of the project/sprint",
        'issues': "Total number of issues", 
        'avg_groupsize': "Average number of members involved in issue discussions", 
        'threeplus_percent': "Percentage of issues with three or more team members", 
        'firefight_percent': "Percentage of issues that are marked emergency or epic", 
        'ownership_percent': "Percentage of issues for which the team member was the assignee or took ownership to deliver", 
        'delivery_percent': "Percentage of issues owned by member that were fixed or resolved", 
        'instability': 'Project instability based on the amount of firefighting that needed to be done to make it work. Low < 20% firefighting issues, high >= 80%, and rest is regular',
        "complexity": "Estimate of difficulty of the project in terms of the number of issues. High >= 80th percentile across all projects, Low <= 20th percentile, normal otherwise", 
        "instability": "Estimate of instability in the project in terms of the number of firefighting issues as a proportion of all issues. High >= 80th percentile across all projects, Low <= 20th percentile, normal otherwise", 
        'collaboration_level': "Estimation of collaboration based on the percent of issues with three or more participants. High >= 70% percentile across all projects, normal otherwise", 
        "group_size": "Average number of team members involved per issue", 
        'threeplus_group_percent':  "Percentage of issues with three or more participants", 
    }
    
def annotate_issue(issue):

    # How much discussion was there. 
    historylen = sum(issue['discussants'].values())
    issue['discussionlen'] = historylen

    # Whether more than two member collaborated (two being typical)
    # opener and closer
    issue['groupsize'] = len(issue['discussants'])

    # Type of issue 
    issue['firefight'] = 1 if issue['issuetype'] in ['Emergency', 'Epic'] else 0
    issue['stability'] = 1 if issue['issuetype'] in ['Bug', 'Regular', 'Internal Task'] else 0
    issue['skilled'] = 1 if issue['issuetype'] in ['Design'] else 0
    

def gather_project_issues(project):

    name = project['name']

    summary = {
        'issues': [],
        'members': [],
        'components': []
    }

    for issue in project['issues']:

        history = issue['history'] 

        issue_summary = OrderedDict([
            ['project', name],
            ['issueid', issue['externalId']],
            ['issuetype', issue['issueType']],
            ['status', issue['status']],
            ['resolution', issue.get('resolution',None)],
            ['priority', issue['priority']],
            ['assignee', issue.get('assignee',None)],
            ['reporter', issue['reporter']],
            ['watchers', issue['watchers']],
            ['components', issue['components']], 
        ])

        # Process the member involved.        
        discussants = [h['author'] for h in history]
        discussants = { d: discussants.count(d) \
                        for d in list(set(discussants))} 
        issue_summary['discussants'] = discussants
        components = issue['components']
        members = [issue['reporter']] + issue['watchers'] + \
                 list(discussants.keys())
        issue_summary['members'] = members

        # Now insert the response time
        responses = {} 
        for i in range(len(history)):
            if i == 0: # ignore the first.
                continue
            curr = history[i]
            prev = history[i-1]
            author = curr['author'] 

            # See how the member to responds to posts from others..
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
        
        summary['members'].extend(members)
        summary['components'].extend(components) 
        summary['issues'].append(issue_summary)

    # Cleanup 
    summary['issues'] = pd.DataFrame(summary['issues'])
    summary['members'] = list(set(summary['members']))
    summary['components'] = list(set(summary['components']))
    
    return summary

def gather_issues(rawdata):

    results = [] 
    for project in rawdata['projects']:
        result = gather_project_issues(project)
        results.append(result)

    issuedf = pd.concat([r['issues'] for r in results])

    # Flatten member
    members = []
    for r in results:
        members.extend(r['members'])
    member = list(set(members))

    return issuedf, members

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

    def compute_instability(percent):
        if percent <= threshold2:
            return 'low'
        elif percent >= threshold1:
            return 'high'
        else:
            return 'normal'     
    projectdf.loc[:, 'instability'] = projectdf['firefight_percent'].apply(compute_instability)
  
    threshold1 = projectdf['threeplus_group_percent'].quantile(0.7)
    def compute_collaboration(percent):
        if percent > threshold1:
            return 'high'
        else:
            return 'normal' 
        
    projectdf.loc[:, 'collaboration_level'] = projectdf['threeplus_group_percent'].apply(compute_collaboration)    


    projectdf = projectdf[['project',
                           'complexity', 'instability', 'collaboration_level',
                           'issues', 'group_size', 'threeplus_group_percent',
                           'firefight_percent']]
    
    return projectdf 

def generate_member_summary(df, member):
    """
    """

    # Which rows are relevant
    df = df[df['members'].apply(lambda members: member in members)]

    # Total issues 
    issues = df.shape[0] 

    firefights = df['firefight'].sum()

    ownership = df[df['assignee'] == member].shape[0]

    successful = df[(df['assignee'] == member) &
                    (df['resolution'].isin(['Fixed', 'Resolved']))].shape[0]

    groupsize = df['groupsize'].mean().round(1)
    threeplus = df[df['groupsize'] > 2].shape[0]

    
    # Firefighter
    # Collaborative
    # Skilled 
    # Takes Ownership 
    # Responsive
    return OrderedDict([
        ['member', member],
        ['issues', issues],
        ['avg_groupsize', groupsize],
        ['threeplus_percent', round(100*threeplus/issues,1)],
        ['firefight_percent', round(100*firefights/issues,1)],
        ['ownership_percent', round(100*ownership/issues,1)],
        ['delivery_percent', round(100*successful/ownership,1)],
    ])
    
    
def generate_members_summary(issuedf, projectdf):

    df = pd.merge(issuedf,
                  projectdf,
                  how='inner',
                  left_on = 'project',
                  right_on = 'project')

    # Gather unique member 
    members = list(df['members'].values)
    members = list(set([member for subset in members for member in subset]))
    
    results = [] 
    for member in members: 
        result = generate_member_summary(df, member) 
        results.append(result)

    df = pd.DataFrame(results)
    return df

def compute(filename):

    # Load rawdata 
    rawdata = json.load(open(filename))

    # Gather issues 
    issuedf, member = gather_issues(rawdata)

    projectdf = generate_project_summary(issuedf) 

    memberdf = generate_members_summary(issuedf, projectdf) 

    return [
        {
            'name': 'issues', 
            'df': issuedf,
            'documentation': get_documentation()
        },
        {
            'name': 'project',
            'df': projectdf,
            'documentation': get_documentation()
        },
        {
            'name': 'member',
            'df': memberdf,
            'documentation': get_documentation()
        }
    ]
