from downloadstockdata import downloadStockBySymbol
from loaddataseries import load_time_series_daily
import matplotlib.pyplot as plt 

downloadStockBySymbol("CRON") # This downloads the time ticker data

# tickerData = load_time_series_daily("AMD") # Generates sequential data




    


# # # line 1 points 
# x1 = range(0, len(tickerData));
# y1 = tickerData;
# # plotting the line 1 points 
# plt.plot(x1, y1, label = "line 1") 

# plt.show() 

