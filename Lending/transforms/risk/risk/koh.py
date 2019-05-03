# Modified code from here..
# http://www.kohkodes.com/posts/2017-04-10-lendingclub/
# Dataset is here http://web.archive.org/web/20140706042617/https://www.lendingclub.com/info/download-data.action

import re
import numpy as np
import pandas as pd
from datetime import datetime

def analysis(df):
    """
    Loan dataframe 
    """

    loan = df

    #Dump rows where policy_code is NaN or 2
    lpc = loan['policy_code']
    loan = loan[~(loan['policy_code'].isnull() | (loan['policy_code'] == 2))]
    loan = loan.drop('policy_code', axis=1)
    # Fix the not very helpful information added to loan_status for some rows
    loan['loan_status'] = loan['loan_status'].map(lambda x: x.replace('Does not meet the credit policy.  Status:', ''))

    loan['id'] = loan['id'].astype(int)

    # Sort columns. Put ids first, followed by date fields, followed by everything else in alphabetical order
    loan = loan[list(loan.columns[:2]) + \
                sorted([x for x in loan.columns[2:] if re.match('.*_d$', x)]) + \
                sorted([x for x in loan.columns[2:] if not re.match('.*_d$', x)])]

    # Convert dates using python datetime instead of pandas because pandas datetimes are not very good
    loan['int_rate'] = loan['int_rate'].map(lambda x: float(x.strip().strip('%'))/100)
    loan.ix[~loan['revol_util'].isnull(), 'revol_util'] = loan.ix[~loan['revol_util'].isnull(), 'revol_util'].map(lambda x: float(x.strip().strip('%'))/100)
    loan['revol_util'] = loan['revol_util'].astype(np.float64)

    loan['earliest_cr_line'] = loan['earliest_cr_line'].map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M').timestamp() if type(x) == str else np.nan)
    loan['accept_d'] = loan['accept_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    loan['exp_d'] = loan['exp_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    loan['list_d'] = loan['list_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    loan['issue_d'] = loan['issue_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    loan['last_pymnt_d'] = loan['last_pymnt_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    loan['next_pymnt_d'] = loan['next_pymnt_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    loan['last_credit_pull_d'] = loan['last_credit_pull_d'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp() if type(x) == str else np.nan)
    
    return loan 
