# StockMarketView-Website
## Visualization and Estimation of Candlestick Patterns in Stock Market
Website - https://stockmarketview.herokuapp.com/
Web app for Stock Market built using dash and plotly in Python.

Features:

plot NSE and BSE stocks for any time period and interval
plot engulfing patterns
plot financial indicators
compare diferent stocks
Multiple time frames
 
## Important Dependencies:

Dash
Plotly
yFinance
sklearn
talib (see the requirements.txt file for complete dependencies)

## Installing Ta-Lib:

download the appropriate whl file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip instal .whl file in the working directory (complete procedure - https://blog.quantinsti.com/install-ta-lib-python/)
Steps for installing the project:

Clone this repository
Install the libraries from requirements.txt
execute the main.py file to run the visualization dash app
the dash app can be accessed on localhost http://127.0.0.1:8050/ on any browser
execute the ml_randForest.py file to obtain the machine learning model
The Dash app is deployed via the heroku platform
