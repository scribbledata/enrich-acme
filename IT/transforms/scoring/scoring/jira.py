import os
import sys
import json
import pandas as pd
from scipy import stats
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
        "issue_percent": "Percent of total issues that involved the team member in some way",
        'avg_groupsize': "Average number of members involved in issue discussions",
        "avg_groupsize_quantile": "For a given member, the quantile of the his/her avg_groupsize",
        'avg_response_time': "Average time (in days) when the team member responded to others' posts",
        "firefight": "Whether issuetype as Emergency or Epic",
        "stability": "Whether issuetype was Bug, Emergency, Epic",
        "skilled": "Whether the issue involved design thinking",
        'threeplus_percent': "Percentage of issues with three or more team members",
        'firefight_percent': "Percentage of issues that are marked emergency or epic",
        'ownership_percent': "Percentage of issues in which the team member participated and in which the team member was the assignee or took ownership to deliver",
        'ownership_percentile': "Percentile of the percentage of issues in which the team member participated and in which the team member was the assignee or took ownership to deliver",
        'delivery_percent': "Percentage of issues owned by member that were fixed or resolved",
        'instability': 'Project instability based on the amount of firefighting that needed to be done to make it work. Low < 20% firefighting issues, high >= 80%, and rest is regular',
        "complexity": "Estimate of difficulty of the project in terms of the number of issues. High >= 80th percentile across all projects, Low <= 20th percentile, normal otherwise",
        "instability": "Estimate of instability in the project in terms of the number of firefighting issues as a proportion of all issues. High >= 80th percentile across all projects, Low <= 20th percentile, normal otherwise",
        'collaboration_level': "Estimation of collaboration based on the percent of issues with three or more participants. High >= 70% percentile across all projects, normal otherwise",
        "groupsize": "Average number of team members involved per issue",
        'threeplus_group_percent':  "Percentage of issues with three or more participants",

        'issueid': "Unique ID for each issue",
        'issuetype': "Type of issue: Bug, New Feature, Regular, Emergency, Improvement, Internal Task, Design, Epic",
        'status': "Status of the issue: Closed, Open, In Progress, Resolved, Reopened",
        'resolution': "How the issue ended: Fixed, Wont Fix, Cannot Reproduce, Duplicate, Incomplete, Resolved",
        'priority': "Priority of the issue: Major, Minor",
        'assignee': "Team member who owns the solution implementation",
        'reporter': "Team member who opened the issue",
        'watchers': "Team members who are tracking the issue",
        'components': "Project components touched by the issue",
        "discussants": "Number of team members involved in the issue",
        "discussion_length": "Number of updates that the issue has seen",
        "members": "Team members who participated in a given issue",
        "responses": "Average response time to another team member's post when there was a response",
        "groupsize": "Number of team members who participated in a given issue",

        "firefighting_ability": "Participation in the firefighting. high >= 80th percentile, low <= 20th percentile",
        "responsiveness": "Responsiveness to peers-message when it happened.  high >= 80th percentile, low <= 20th percentile",
        "responsiveness_quantile": "For each member, percentile of average response time across all members",
        "collaborativeness": "Engagement with peers in terms of the avg team size when this team member was involved in issue resolution.  high >= 80th percentile, low <= 20th percentile",
        "delivery_ability": "Ability to complete tasks assigned to the member. high >= 80th percentile, low <= 20th percentile",
    }

def annotate_issue(issue):

    # How much discussion was there.
    historylen = sum(issue['discussants'].values())
    issue['discussion_length'] = historylen

    # Whether more than two member collaborated (two being typical)
    # opener and closer
    issue['groupsize'] = len(issue['discussants'])

    # Type of issue
    issue['firefight'] = 1 if issue['issuetype'] in ['Emergency', 'Epic'] else 0
    issue['stability'] = 1 if issue['issuetype'] in ['Bug', 'Emergency', 'Epic'] else 0
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
            'groupsize': groupsize,
            'threeplus_group_percent': round(100*threeplus/issues,1),
        })

    projectdf = issuedf.groupby('project').apply(summarize)
    projectdf = projectdf.reset_index()

    eighty = projectdf['issues'].quantile(0.8)
    twenty = projectdf['issues'].quantile(0.2)

    def compute_complexity(count):
        if count <= twenty:
            return 'low'
        elif count >= eighty:
            return 'high'
        else:
            return 'normal'
    projectdf.loc[:, 'complexity'] = projectdf['issues'].apply(compute_complexity)

    eighty = projectdf['firefight_percent'].quantile(0.8)
    twenty = projectdf['firefight_percent'].quantile(0.2)

    def compute_instability(percent):
        if percent <= twenty:
            return 'low'
        elif percent >= eighty:
            return 'high'
        else:
            return 'normal'
    projectdf.loc[:, 'instability'] = projectdf['firefight_percent'].apply(compute_instability)

    seventy = projectdf['threeplus_group_percent'].quantile(0.7)
    def compute_collaboration(percent):
        if percent >= seventy:
            return 'high'
        else:
            return 'normal'

    projectdf.loc[:, 'collaboration_level'] = projectdf['threeplus_group_percent'].apply(compute_collaboration)


    projectdf = projectdf[['project',
                           'complexity', 'instability', 'collaboration_level',
                           'issues', 'groupsize', 'threeplus_group_percent',
                           'firefight_percent']]

    return projectdf

def generate_member_summary(completedf, member):
    """
    """

    # Which rows are relevant
    df = completedf[completedf['members'].apply(lambda members: member in members)]

    # Total issues
    issues = df.shape[0]
    projects = df['project'].nunique()
    firefights = df['firefight'].sum()
    ownership = df[df['assignee'] == member].shape[0]
    successful = df[(df['assignee'] == member) &
                    (df['resolution'].isin(['Fixed', 'Resolved']))].shape[0]

    groupsize = df['groupsize'].mean().round(1)
    threeplus = df[df['groupsize'] > 2].shape[0]


    # => Responsiveness
    responses = [responses[member] \
        for responses in list(df['responses'].values) \
           if member in responses]

    if len(responses) > 0:
        avg_response_time = round(sum(responses)/len(responses),1)
    else:
        avg_response_time = None

    # Firefighter
    # Collaborative
    # Skilled
    # Takes Ownership
    # Responsive
    return OrderedDict([
        ['member', member],
        ['projects', projects], 
        ['issues', issues],
        # ['total_issues', completedf.shape[0]],
        ['issue_percent', round(100*issues/completedf.shape[0],2)],
        ['avg_groupsize', groupsize],
        ['threeplus_percent', round(100*threeplus/issues,1)],
        ['firefight_percent', round(100*firefights/issues,1)],
        ['ownership_percent', round(100*ownership/issues,1)],
        ['delivery_percent', round(100*successful/ownership,1)],
        ['avg_response_time', avg_response_time]
    ])

def generate_members_summary(issuedf, projectdf):

    # Filter out unnecessary columns and conflicting columns such as group size
    projectdf = projectdf[['project', 'complexity', 'instability', 'collaboration_level']]

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

    #=> Insert firefighting ability
    eighty = df['firefight_percent'].quantile(0.8)
    twenty = df['firefight_percent'].quantile(0.2)
    def compute_firefighting_ability(percent):
        if percent <= twenty:
            return 'low'
        elif percent >= eighty:
            return 'high'
        else:
            return 'normal'

    df.loc[:, 'firefighting_ability'] = df['firefight_percent'].apply(compute_firefighting_ability)

    #=> responsiveness
    eighty = df['avg_response_time'].quantile(0.8)
    twenty = df['avg_response_time'].quantile(0.2)
    def compute_responsiveness(value):
        if pd.isnull(value):
            return "unknown"
        elif value <= twenty:
            return 'high'
        elif value >= eighty:
            return 'low'
        else:
            return 'normal'
    df.loc[:, 'responsiveness'] = df['avg_response_time'].apply(compute_responsiveness)

    def responsetime_percentile(x):
        if pd.isnull(x):
            return None
        else:
            return round(stats.percentileofscore(df['avg_response_time'].dropna(),x))
    df.loc[:, 'responsiveness_quantile'] = df['avg_response_time'].apply(responsetime_percentile)

    #=> collaborativeness
    eighty = df['avg_groupsize'].quantile(0.8)
    twenty = df['avg_groupsize'].quantile(0.2)
    def compute_collaborativeness(value):
        if pd.isnull(value):
            return "unknown"
        elif value <= twenty:
            return 'low'
        elif value >= eighty:
            return 'high'
        else:
            return 'normal'
    df.loc[:, 'collaborativeness'] = df['avg_groupsize'].apply(compute_collaborativeness)


    alpha = lambda x: None if pd.isnull(x) else round(stats.percentileofscore(df['avg_groupsize'].dropna(),x))
    df.loc[:, 'avg_groupsize_quantile'] = df['avg_groupsize'].apply(alpha)

    #=> Insert firefighting ability
    eighty = df['delivery_percent'].quantile(0.8)
    twenty = df['delivery_percent'].quantile(0.2)
    def compute_delivery_ability(percent):
        if percent <= twenty:
            return 'low'
        elif percent >= eighty:
            return 'high'
        else:
            return 'normal'

    df.loc[:, 'delivery_ability'] = df['delivery_percent'].apply(compute_delivery_ability)
    beta = lambda x: None if pd.isnull(x) else round(stats.percentileofscore(df['delivery_percent'].dropna(),x))
    df.loc[:, 'delivery_quantile'] = df['delivery_percent'].apply(beta)

    #=> Ownership ability
    eighty = df['ownership_percent'].quantile(0.8)
    twenty = df['ownership_percent'].quantile(0.2)
    def compute_owning_ability(value):
        if pd.isnull(value):
            return "unknown"
        elif value <= twenty:
            return 'low'
        elif value >= eighty:
            return 'high'
        else:
            return 'normal'
    df.loc[:, 'ownership_ability'] = df['ownership_percent'].apply(compute_owning_ability)


    theta = lambda x: None if pd.isnull(x) else round(stats.percentileofscore(df['ownership_percent'].dropna(),x))
    df.loc[:, 'ownership_quantile'] = df['ownership_percent'].apply(theta)

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
            'name': 'issue',
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
