class TickerSelector:
    def __init__(self, openKey, closeKey, lowKey, highKey, volumeKey): 
        self.open = openKey
        self.close = closeKey
        self.low = lowKey
        self.high = highKey
        self.volume = volumeKey



alphaVantage = TickerSelector("1. open", "4. close", "3. low", "2. high", "5. volume")
polygonIo = TickerSelector("o", "c", "l", "h", "v")
tingo = TickerSelector("open", "close", "low", "high", "volume")

