import yfinance as yf
print("yfinance imported successfully")
try:
    # Test a simple collection
    t = yf.Ticker("AAPL")
    hist = t.history(period="1d")
    print(hist)
except Exception as e:
    print(f"Error: {e}")
