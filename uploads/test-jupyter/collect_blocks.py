import os
import pymysql
import pandas.io.sql as sql
import pandas as pd
from tqdm import tqdm_notebook

connection = pymysql.connect(host='localhost',
                             user=os.getenv('CF_DB_USER', 'root'),
                             password=os.getenv('MYSQL_PASS', 'pass'),
                             db=os.getenv('CF_DB', 'testcf'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
connection.commit()

df_user = sql.read_sql("select * from participant", connection)
df_acc = sql.read_sql("select * from acceptance", connection)


index = []
stat_list = []
usernum_list = []
filenum_list = []


rating_split = [
    1100, 1200, 1300, 1400, 1500, 1600, 1700, 1900, 2200, 9999
]
rating_split_bin = [-1000] + rating_split
rating_label = ['%d - %d' % (s + 1, t) for s, t in zip(rating_split_bin, rating_split_bin[1:])]
rating_label[0] = ' - 1100'
rating_label[-1] = '2200 - '

acceptance_split = [0.2 * i for i in range(6)]

group_tag = ['block_type', 'parent_type', 'modification_type', 'rating_bin']

probs = sql.read_sql('select * from problem', connection)

for p in tqdm_notebook(probs['problem_id']):
    """
    block_type, node_typeを要素とするSeriesを作成
    indexは問題id
    """
    df_prob = sql.read_sql("select * from modification where problem_id='%s'" % p, connection)
    df_prob = df_prob.merge(df_user)
    rating_bin = pd.cut(df_prob.rating, rating_split_bin, labels=rating_label)
    df_prob['rating_bin'] = rating_bin
    stat = df_prob.groupby(group_tag).size().fillna(0)
    stat_list.append(stat)
    index.append(p)
    grouped = df_prob.groupby(['rating_bin'])
    users = grouped.user_name.agg(lambda x: x.nunique())
    files = grouped.file_name.agg(lambda x: x.nunique())
    usernum_list.append(users)
    filenum_list.append(files)

stat_df = pd.DataFrame(stat_list, index=index).fillna(0)
stat_df.to_csv('stat_with_rating_par.csv')

user_num = pd.DataFrame(usernum_list, index=index).fillna(0)
file_num = pd.DataFrame(filenum_list, index=index).fillna(0)

user_num.to_csv('user_num.csv')
file_num.to_csv('file_num.csv')
