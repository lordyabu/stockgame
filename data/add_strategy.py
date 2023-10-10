# import pandas as pd
# import numpy as np
#
# df_name = './Day1/PriceDay1.csv'
# df_name1 = './Day1/PriceDay2.csv'
# df_name2 = './Day1/PriceDay3.csv'
#
# df = pd.read_csv(df_name, index_col=[0])
# df1 = pd.read_csv(df_name1, index_col=[0])
# df2 = pd.read_csv(df_name2, index_col=[0])
#
# print(df2['Price'].iloc[11])
# print(df1['Price'].iloc[11])
# print(df['Price'].iloc[11])
#
# df['Price1'] = df['Price'].values
# df['Price2'] = df1['Price'].values
# df['Price3'] = df2['Price'].values
#
#
# df.to_csv('Day1.csv')
#
# print(df['Price1'].iloc[11])
# print(df['Price2'].iloc[11])
# print(df['Price3'].iloc[11])