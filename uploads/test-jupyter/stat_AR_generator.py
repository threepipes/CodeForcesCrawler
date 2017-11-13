import pandas as pd
import os
import pymysql
import pandas.io.sql as sql
from logging import getLogger, INFO

logger = getLogger(__file__)
logger.setLevel(INFO)


logger.info('start acc_rating_stat generator')

stat_df = pd.read_csv('only_condition.csv',  # 'stat_with_rating_par.csv',
                      index_col=[0],
                      header=[0, 1, 2, 3],
                      skipinitialspace=True,
                      tupleize_cols=True)
stat_df.columns = pd.MultiIndex.from_tuples(stat_df.columns)

connection = pymysql.connect(host='localhost',
                             user=os.getenv('CF_DB_USER', 'root'),
                             password=os.getenv('MYSQL_PASS', 'pass'),
                             db=os.getenv('CF_DB', 'testcf'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
connection.commit()

logger.info('succeeded connecting db')

df_acc = sql.read_sql("select * from acceptance", connection)
df_acc.index = df_acc.problem_id

acceptance_split = [0.2 * i for i in range(6)]
label = [0.2 * (i + 1) for i in range(5)]
acc_bin = pd.cut(df_acc.acceptance_rate, acceptance_split, labels=label)

stat_df['acceptance_bin'] = acc_bin
acc_count = acc_bin.value_counts()


def generate_stat_file(side):
    logger.info('starting %s side' % side)
    num = pd.read_csv('%s_num.csv' % side, index_col=0)
    dived = stat_df.div(num, axis=1, level=3).fillna(0)
    dived['acceptance_bin'] = acc_bin
    dived_gp = dived.groupby('acceptance_bin').sum()
    dived_gp_div = dived_gp.div(acc_count, axis=0)
    dived_gp.to_csv('dived_%s_gp.csv' % side)
    dived_gp_div.to_csv('dived_%s_gp_norm.csv' % side)


logger.info('prepared needed dataframe')
logger.info('generating stat files')

generate_stat_file('user')
generate_stat_file('file')
