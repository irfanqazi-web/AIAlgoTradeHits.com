# Testing Instructions

## Current Status

✅ **API Server Running**: http://localhost:8080
✅ **React App Running**: http://localhost:5173
✅ **Timestamps Fixed**: All API endpoints returning correct Unix timestamps

## How to Test

### 1. Open the Application
Navigate to: **http://localhost:5173**

### 2. Test Crypto Charts (BTC/USD)
- Click on "Crypto" market type
- You should see Bitcoin (BTC/USD) data
- Try switching between timeframes:
  - **Daily** - Should show ~720 days of data
  - **Hourly** (15min) - Should show ~384 candles (4 days)
  - **5min** - Should show ~576 candles (2 days)

### 3. Test Stock Charts (NVDA)
- Click on "Stock" market type
- You should see NVIDIA (NVDA) data
- Try switching between timeframes:
  - **Daily** - Should show ~5000 days of data
  - **Hourly** (15min) - Should show ~104 candles (4 days)
  - **5min** - Should show ~156 candles (2 days)

### 4. Check Browser Console
Open browser DevTools (F12) and check the Console tab for:

✅ **Expected logs:**
```
✓ Crypto daily response: {success: true, count: 720, ...}
✓ Transformed 720 crypto daily candles for BTC/USD
TradingView chart loaded 720 candles for BTC/USD (daily)
```

❌ **Look for errors:**
- HTTP errors (404, 500, etc.)
- Data transformation errors
- Chart rendering errors

### 5. Test API Directly (Optional)
Open in browser or use curl:

**Stock Endpoints:**
- http://localhost:8080/api/stocks/history?symbol=NVDA&limit=10
- http://localhost:8080/api/stocks/15min/history?symbol=NVDA&limit=10
- http://localhost:8080/api/stocks/5min/history?symbol=NVDA&limit=10

**Crypto Endpoints:**
- http://localhost:8080/api/crypto/daily/history?pair=BTC/USD&limit=10
- http://localhost:8080/api/crypto/15min/history?pair=BTC/USD&limit=10
- http://localhost:8080/api/crypto/5min/history?pair=BTC/USD&limit=10

## Known Issues Based on Your Screenshots

### Crypto
- ✅ **Hourly works** - Using 15min data successfully
- ❌ **Daily not working** - Check console for errors
- ❌ **5min not working** - Check console for errors

### Stock
- ✅ **Hourly works** - Using 15min data successfully
- ✅ **5min works** - Should be showing data
- ❌ **Daily not working** - Check console for errors

## What to Look For

1. **Empty Charts**: If chart shows but no data:
   - Check browser console for API errors
   - Verify data is being fetched (network tab)
   - Check if timestamps are valid

2. **No Chart Rendering**: If chart area is blank:
   - Check for JavaScript errors in console
   - Verify lightweight-charts is loading
   - Check CSS/styling issues

3. **Wrong Data**: If chart shows but wrong timeframe:
   - Check which endpoint is being called (network tab)
   - Verify timeframe parameter is correct

## Next Steps After Testing

Once you've identified which specific charts aren't working:
1. Take a screenshot of the browser console
2. Note which timeframe/market combination fails
3. We'll debug the specific issue together

## Debugging Tips

**Enable verbose logging:**
```javascript
// In browser console:
localStorage.setItem('debug', '*');
```

**Check what data the API is returning:**
```javascript
// In browser console:
fetch('http://localhost:8080/api/crypto/daily/history?pair=BTC/USD&limit=5')
  .then(r => r.json())
  .then(console.log)
```

**Verify timestamps:**
```javascript
// Timestamps should be around 1700000000-1730000000 (2023-2024)
// NOT future dates like 1763340300
```
