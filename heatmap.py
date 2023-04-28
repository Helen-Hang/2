import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('./data.csv')#这里的data.csv为任意csv文件
data = df.values
f,ax=plt.subplots(figsize=(4,2))
fig=sns.heatmap(df,annot=True,fmt='.2g',cmap='YlOrRd', cbar=False,linewidths= .5)
y = range(0,2,1)
plt.yticks(y,('Evidence','S-weight'))
plt.savefig("./fig9-2.pdf")
plt.show()
