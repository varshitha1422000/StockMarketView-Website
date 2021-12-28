import yfinance as yf
import talib
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn import tree
import numpy as np
from sklearn.metrics import plot_confusion_matrix
from collections import Counter
from imblearn.over_sampling import RandomOverSampler
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

tick = yf.Ticker("RELIANCE.NS")
df = tick.history('10y', '1d')
# print(df.isnull().sum())
df = df.dropna()
# df.drop(['Volume', 'Dividends', 'Stock Splits'], inplace=True, axis=1)
df['Engulfing'] = talib.CDLENGULFING(df['Open'], df['High'], df['Low'], df['Close'])
# df.drop(['Low', 'High'], inplace=True, axis=1)
print(df.head())

feature = ['Open', 'High', 'Low', 'Close']
target = 'Engulfing'
X = df[feature]
y = df[target]
print(Counter(y))

ros = RandomOverSampler()
X_ros, y_ros = ros.fit_resample(X, y)
print(Counter(y_ros))

X_train, X_test, y_train, y_test = train_test_split(X_ros, y_ros, test_size=0.2, random_state=50)

model_rfc = RandomForestClassifier(n_estimators=70).fit(X_train, y_train)
y_pred_rfc = model_rfc.predict(X_test)
print("Model Accuracy:", metrics.accuracy_score(y_test, y_pred_rfc))
print("Confusion matrix:\n", metrics.confusion_matrix(y_test, y_pred_rfc))

plt.figure(figsize=(30, 10))
_ = tree.plot_tree(model_rfc.estimators_[0], feature_names=X.columns, filled=True)
plt.show()
