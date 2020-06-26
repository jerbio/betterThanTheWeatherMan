from pyrh import Robinhood

rh = Robinhood()
rh.login(username="YOUR_EMAIL", password="YOUR_PASSWORD")
rh.print_quote("AAPL")

