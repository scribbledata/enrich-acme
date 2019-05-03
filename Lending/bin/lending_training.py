# Modified code from here..
# http://www.kohkodes.com/posts/2017-04-10-lendingclub/
# Dataset is here http://web.archive.org/web/20140706042617/https://www.lendingclub.com/info/download-data.action

import re
import numpy as np
import pandas as pd
from datetime import datetime
import os
from functools import reduce
from datetime import datetime
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from sklearn.preprocessing import RobustScaler, MinMaxScaler, StandardScaler
from scipy.spatial.distance import pdist, squareform
import mlflow
import mlflow.sklearn


pd.set_option('display.max_columns', 100)

input_data_loc = os.environ["MLFLOW_DATA"]

loan = pd.read_csv(os.path.join(input_data_loc,'Loans.csv'),low_memory=False)
# loan = pd.read_csv('LoanStats3a.csv')



# Dump rows where policy_code is NaN or 2
lpc = loan['policy_code']
loan = loan[~(loan['policy_code'].isnull() | (loan['policy_code'] == 2))]
loan = loan.drop('policy_code', axis=1)
# Fix the not very helpful information added to loan_status for some rows
loan['loan_status'] = loan['loan_status'].map(lambda x: x.replace('Does not meet the credit policy.  Status:', ''))
loan['id'] = loan['id'].astype(int)
# Sort columns. Put ids first, followed by date fields, followed by everything else in alphabetical order
loan = loan[list(loan.columns[:2]) + sorted([x for x in loan.columns[2:] if re.match('.*_d$', x)]) + sorted([x for x in loan.columns[2:] if not re.match('.*_d$', x)])]


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

print('# unique emp_title =', len(loan['emp_title'].unique()))
print('# unique url =', len(loan['url'].unique()))
print('# unique desc =', len(loan['desc'].unique()))
print('# unique title =', len(loan['title'].unique()))
print('# unique addr_city =', len(loan['addr_city'].unique()))

print('\n=========Loan status==========')
print(
    '\n'.join(str(
        loan['loan_status'].value_counts().sort_index() / len(loan)
    ).split('\n')[:-1])
)
print(loan.ix[loan['next_pymnt_d'].isnull(), 'loan_status'].unique())
print(loan.ix[loan['next_pymnt_d'].isnull(), 'loan_status'].count())

# Make the dataset to train on
Y = (loan.ix[loan['next_pymnt_d'].isnull(), 'loan_status'] == 'Charged Off').astype(int)
Y.reset_index(drop=True, inplace=True)
X = loan[loan['next_pymnt_d'].isnull()].drop(['next_pymnt_d', 'loan_status', 'emp_title', 'url', 'desc', 'title', 'addr_city'], axis=1)
for c in X.columns:
    if X[c].dtype == 'O':
        X[c] = X[c].astype('category')
X.reset_index(drop=True, inplace=True)
cat = pd.concat((X,Y), join='inner', axis=1)


for c in X.columns:
    if len(X[c].unique()) == 1:
        print('Dropping {}'.format(c))
        X = X.drop(c, axis=1)

# Find where the first block of nans ends
period = [
    next(x for x in X.iterrows() if ~np.isnan(x[1]['pub_rec_bankruptcies']))[0],
    next(x for x in X.iterrows() if ~np.isnan(x[1]['total_bal_ex_mort']))[0],
    next(x for x in X.iterrows() if ~np.isnan(x[1]['num_sats']))[0],
    next(x for x in X.iterrows() if ~np.isnan(x[1]['num_tl_op_past_12m']))[0]
]

period0_vars = {'pub_rec_bankruptcies'}
period1_vars = set(['acc_open_past_24mths', 'bc_open_to_buy', 'percent_bc_gt_75',
               'bc_util', 'mths_since_recent_inq',
               'mths_since_recent_revol_delinq', 'mths_since_recent_bc',
               'mort_acc', 'total_bal_ex_mort', 'total_bc_limit'])
period2_vars = set(['num_sats', 'num_bc_sats'])
period3_vars = set(['total_il_high_credit_limit', 'num_rev_accts',
               'mths_since_recent_bc_dlq', 'num_accts_ever_120_pd',
               'mths_since_last_major_derog', 'num_tl_op_past_12m',
               'mo_sin_rcnt_tl', 'tot_hi_cred_lim', 'tot_cur_bal',
               'avg_cur_bal', 'num_bc_tl', 'num_actv_bc_tl', 'pct_tl_nvr_dlq',
               'num_tl_90g_dpd_24m', 'num_tl_30dpd', 'num_tl_120dpd_2m',
               'num_il_tl', 'mo_sin_old_il_acct', 'num_actv_rev_tl',
               'mo_sin_old_rev_tl_op', 'mo_sin_rcnt_rev_tl_op',
               'total_rev_hi_lim', 'num_rev_tl_bal_gt_0', 'num_op_rev_tl',
               'tot_coll_amt'])

new_cols = list(X.columns[np.array((0,1,2,3,4,7))]) + list(X.columns[np.array((5,6))]) + list(X.columns[8:])
new_cols[6:] = sorted(period0_vars) + sorted(period1_vars) + sorted(period2_vars) + sorted(period3_vars) + sorted(list(set(new_cols[6:]) - (period0_vars | period1_vars | period2_vars | period3_vars)))

assert(sorted(new_cols) == sorted(X.columns))

X = X[new_cols]

def visualize_df(df):
    viridis = plt.cm.viridis
    viridis.set_bad((.7, 0, 0))
    fig, ax = plt.subplots(1,1)
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.name == 'category':
            df[c] = df[c].cat.codes
        if df[c].dtype.name == 'bool':
            df[c] = df[c].astype(int)
        if (df[c].max() - df[c].min()) != 0:
            df[c] = (df[c] - df[c].min())/(df[c].max() - df[c].min())

    ax.imshow(df.T, cmap=viridis)
    ax.yaxis.set_tick_params(which='minor', length=0)
    ax.set_yticks(np.array(range(len(df.columns)))+.5)
    ax.set_yticks(np.array(range(len(df.columns))), minor=True)
    ax.set_yticklabels([])
    ax.set_yticklabels(df.columns, minor=True, fontsize=9)
    ax.grid()
    fig.set_facecolor('w')
    ax.set_aspect('auto')
    fig.set_dpi(100)
    fig.set_size_inches(19.2, 10)
    fig.tight_layout()
    return fig, ax

# fig, ax = visualize_df(X)
# ax.grid(color=('#AAAAAA'))
# plt.show()
# fig.set_size_inches(19.2,10.8)

X['pub_rec_bankruptcies'] = X['pub_rec_bankruptcies'].fillna(0)


def null_dist_map(nulls):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="divide by zero encountered in log")
        logdist = np.log10(squareform(pdist(nulls.T, metric='hamming')) * len(nulls))

    fig, ax = plt.subplots(1,1)
    img = ax.imshow(logdist, cmap=plt.cm.viridis)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(img, cax=cax)
    cax.set_ylabel('log distance', fontsize=10)

    ax.set_xticks([])
    ax.grid(color='#AAAAAA')
    ax.set_yticks(np.arange(len(nulls.columns))+.5)
    ax.set_yticklabels([])
    ax.set_yticks(range(len(nulls.columns)), minor=True)
    ax.set_yticklabels(nulls.columns, fontsize=10, minor=True)
    fig.set_facecolor('w')
    fig.set_size_inches(8,8)
    fig.set_dpi(100)
    fig.tight_layout()
    return fig, ax

# nulls = X.loc[:,X.isnull().sum() > 0].isnull()
# fig, ax = null_dist_map(nulls)
# fig.tight_layout()
# plt.show()

informative_nulls = sorted(['mo_sin_old_il_acct',
                            'mths_since_recent_bc',
                            'mths_since_recent_inq',
                            'mths_since_recent_revol_delinq',
                            'mths_since_last_major_derog',
                            'mths_since_recent_bc_dlq',
                            'mths_since_last_delinq',
                            'mths_since_last_record'])

for c in informative_nulls:
    X[c+'_missing'] = X[c].isnull()

    # Use the variables without informative nulls after their data non-collection periods
    # to indicate which null rows should be considered to be non-informative.
    if c in period1_vars:
        per = X['acc_open_past_24mths'].isnull()
    elif c in period2_vars:
        per = X['num_sats'].isnull()
    elif c in period3_vars:
        per = X['num_il_tl'].isnull()
    else:
        per = slice(0, -1)
    X.loc[per, c+'_missing'] = np.nan
    X.loc[X[c+'_missing'] == 1, c] = 0


# Copy the dataset, drop id and date fields, and fill in missing values from the empirical distribution
X_imp = X.drop(['id', 'member_id', 'accept_d', 'exp_d', 'issue_d', 'list_d'], axis=1)
for c in X_imp.columns:
    valid = X_imp[c].dropna()
    X_imp.loc[X_imp[c].isnull(),c] = np.random.choice(valid, size=X_imp[c].isnull().sum(), replace=True)
    if c.find('missing') != -1:
        X_imp.loc[X_imp[c] == 1, c[:c.find('_missing')]] = 0

cat_cols = set(c for c in X_imp.columns if X_imp[c].dtype.name == 'category')
num_cols = set(c for c in X_imp.columns if X_imp[c].dtype == float)
indicator_cols = set(c for c in X_imp.columns if c.find('_missing') != -1)
cat_cols = cat_cols - indicator_cols
num_cols = num_cols - indicator_cols
assert cat_cols | num_cols | indicator_cols == set(X_imp.columns)

X_scale = pd.concat( (pd.DataFrame(MinMaxScaler().fit_transform(X_imp[sorted(num_cols)]), columns = sorted(num_cols)),
                      pd.get_dummies(X_imp[sorted(cat_cols)]),
                      X_imp[sorted(indicator_cols)]), axis=1 )




def impute_column(target, rows, df):
    """
    Inputs
    ------
    targets : iterable of str
        Variable to impute. If numerical, pass a length one iterable with the name of the column in `df`. If categorical or paired with a missing value indicator, provide names of all the columns.
    rows : boolean indexer for pandas.Series
        Which rows to impute. Will be used like so: df.loc[rows, targets] = ...
    df : pandas.DataFrame
        DataFrame with values to impute
    """
    from sklearn.linear_model import Ridge, LogisticRegression
    for c in target:
        if c not in df.columns:
            raise ValueError('No column named {}'.format(c))
    if rows.shape != (len(df),) or rows.dtype != bool:
        raise ValueError('Rows must be a boolean')

    if len(target) == 1:
        assert np.issubdtype(df[target[0]].dtype, np.number), 'When imputing a single column, the dtype of the column must be numeric.'
        reg = Ridge(alpha=.1)
        train_data = df.loc[~rows, set(df.columns) - set(target)]
        impute_data = df.loc[rows, set(df.columns) - set(target)]
        reg.fit(train_data, df.loc[~rows, target[0]])
        df.loc[rows, target[0]] = reg.predict(impute_data)
    else:
        if len([c for c in target if c.find('_missing') != -1]):
            assert len(target) == 2, 'Missing value indicator variable provided, but len(target) != 2.'

            regression_target_name = [c for c in target if c.find('_missing') == -1][0]
            indicator_target_name = [c for c in target if c.find('_missing') != -1][0]
            train_data = df.loc[~rows, set(df.columns) - set([regression_target_name, indicator_target_name])]
            impute_data = df.loc[rows, set(df.columns) - set([regression_target_name, indicator_target_name])]

            reg = Ridge(alpha=.1)
            ind = LogisticRegression(solver='lbfgs')
            reg.fit(train_data, df.loc[~rows, regression_target_name])
            ind.fit(train_data, df.loc[~rows, indicator_target_name])
            df.loc[rows, indicator_target_name] = ind.predict(impute_data)
            df.loc[rows, regression_target_name] = reg.predict(impute_data) * df.loc[rows, indicator_target_name]
        else:
            reg = LogisticRegression(solver='lbfgs')
            train_data = df.loc[~rows, list(set(df.columns) - set(target))]
            impute_data = df.loc[rows, list(set(df.columns) - set(target))]
            labels = np.argwhere(df.loc[~rows, target].values)[:,1]
            reg.fit(train_data, labels)
            # Manually do encoding instead of get_dummies in case number of unique predictions != number of classes
            prediction = np.zeros(df.loc[rows, target].shape)
            prediction[np.arange(len(prediction)), reg.predict(impute_data)] = 1
            df.loc[rows, target] = prediction

X_scale_c = X_scale.copy()
# print(X_scale_c.columns)
# cols = [i for i in list(range(12))+list(range(12,42))+list(range(43,93))+list(range(93,len(list(X_scale_c.columns))))]
# X_scale_c.drop(X_scale_c.columns[cols],axis=1,inplace=True)
null_cols = set(X.columns[X.isnull().sum() > 0])
null_cols = null_cols - set([c+'_missing' for c in informative_nulls])
max_iter = 1
eps = 1e-3
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URL"])

f = open('feature_file.json', 'w')
f.write(str(list(X_scale_c.columns)))
f.close()
mlflow.log_artifact("feature_file.json","model")
os.remove('feature_file.json')

for i in range(max_iter):
    print('iter', i)
    previous = X_scale_c.copy()
    for n,c in enumerate(null_cols):
        print(n+1, len(null_cols), end='\r')
        if c in informative_nulls:
            target = [c, c+'_missing']
        elif X[c].dtype.name == 'category':
            target = [cc for cc in X_scale_c.columns if re.match('^{}_'.format(c), cc)]
        else:
            target = [c]
        if "emp_length_1" not in target[0]:

            impute_column(target, X[target[0]].isnull(), X_scale_c)
    diff = np.abs(X_scale_c.loc[:,num_cols] - previous.loc[:,num_cols])
    mlflow.log_metric("percentile",(np.percentile(diff, 95)))
    print()
    if np.percentile(diff, 95) < eps:
        break
