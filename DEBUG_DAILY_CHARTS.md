# Debug Daily Charts Issue

## Problem
- ✅ Crypto Hourly (15min) works
- ✅ Stock Hourly (15min) works
- ✅ Stock 5min works
- ❌ Crypto Daily doesn't work
- ❌ Stock Daily doesn't work

## API Tests - All Passing ✅

### Stock Daily
```
Success: True
Count: 1
Has data: True
First timestamp: 1136764800 (Jan 9, 2006)
```

### Crypto Daily
```
Success: True
Count: 1
Has data: True
First timestamp: 1701561600 (Dec 3, 2023)
```

## Possible Causes

### 1. Chart Can't Handle Large Datasets
- Daily charts fetch 550 candles
- Hourly/5min fetch 100-500 candles
- **Test**: Try limiting daily to 100 candles

### 2. Timezone Issues with Daily Data
- Daily data might need special timezone handling
- Stock daily has no timezone, crypto daily has +00:00
- **Test**: Check if timestamps are being interpreted correctly

### 3. Chart Configuration for Daily Timeframe
- Daily charts might need different timeScale settings
- **Test**: Check if timeScale.timeVisible needs adjustment

## Quick Test

Open browser console (F12) and run:

```javascript
// Test stock daily with small dataset
fetch('http://localhost:8080/api/stocks/history?symbol=NVDA&limit=50')
  .then(r => r.json())
  .then(data => {
    console.log('Stock Daily Test:');
    console.log('Count:', data.count);
    console.log('First:', data.data[0]);
    console.log('Last:', data.data[data.data.length-1]);
    console.log('Timestamps range:',
      data.data[0].timestamp,
      'to',
      data.data[data.data.length-1].timestamp
    );
  });
```

```javascript
// Test crypto daily with small dataset
fetch('http://localhost:8080/api/crypto/daily/history?pair=BTC/USD&limit=50')
  .then(r => r.json())
  .then(data => {
    console.log('Crypto Daily Test:');
    console.log('Count:', data.count);
    console.log('First:', data.data[0]);
    console.log('Last:', data.data[data.data.length-1]);
    console.log('Timestamps range:',
      data.data[0].timestamp,
      'to',
      data.data[data.data.length-1].timestamp
    );
  });
```

## What to Check in Browser Console

When you click on Daily timeframe, look for these logs:

1. **API Response:**
   ```
   ✓ Stock daily response: {success: true, count: 550, ...}
   ✓ Transformed 550 stock daily candles for NVDA
   ```

2. **Candle Details:**
   ```
   Candle 0: {datetime: "2006-01-09T00:00:00", timestamp: 1136764800, parsedTime: 1136764800, close: 0.35}
   Candle 1: {datetime: "2006-01-10T00:00:00", timestamp: 1136851200, parsedTime: 1136851200, close: 0.35}
   ```

3. **Transformed Data:**
   ```
   Transformed data: 550 candles, time range: 1136764800 to 1732060800
   ```

4. **Chart Loading:**
   ```
   TradingView chart loaded 550 candles for NVDA (daily)
   ```

## If You See Errors

### "Invalid time" Error
- Means timestamps are not in correct format
- Should be Unix seconds (10 digits like 1701561600)
- NOT milliseconds (13 digits)

### "No data available" Message
- API returned data but chart can't display it
- Check if data.length === 0 after transformation

### Chart Just Blank (No Error)
- Chart might be rendering outside visible range
- timeScale().fitContent() might not be working
- Try manually setting visible range

## Temporary Fix to Test

Let me reduce the daily data limit to see if size is the issue:
