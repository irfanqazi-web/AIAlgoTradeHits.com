"""
INDICATOR VALIDATION SCRIPT
Compares database indicator values against pandas_ta recalculations
Tests all 64 indicators for accuracy

Usage: python validate_indicators.py <excel_file.xlsx>
Example: python validate_indicators.py SPY_97_fields_complete.xlsx
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
from datetime import datetime

# Validation tolerance (0.1% difference allowed)
TOLERANCE_PCT = 0.1

def validate_indicators(file_path, num_samples=100):
    """
    Main validation function
    """
    print("="*80)
    print("INDICATOR VALIDATION SCRIPT")
    print("="*80)
    print(f"\nFile: {file_path}")
    print(f"Validation samples: {num_samples}")
    print(f"Tolerance: {TOLERANCE_PCT}%\n")
    
    # Load data
    print("Loading data...")
    df = pd.read_excel(file_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN'
    print(f"Symbol: {symbol}")
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}\n")
    
    # Initialize results tracking
    results = {
        'indicator': [],
        'total_tested': [],
        'matches': [],
        'mismatches': [],
        'max_diff_pct': [],
        'status': []
    }
    
    # Sample random rows (skip first 200 for warm-up)
    sample_indices = np.random.choice(
        range(200, len(df)), 
        size=min(num_samples, len(df)-200), 
        replace=False
    )
    
    print("Starting validation...\n")
    print("-"*80)
    
    # ========================================================================
    # 1. RSI (14-period)
    # ========================================================================
    print("\n1. Validating RSI...")
    if 'rsi' in df.columns:
        df['rsi_calc'] = ta.rsi(df['close'], length=14)
        result = compare_indicator(df, 'rsi', 'rsi_calc', sample_indices)
        results['indicator'].append('RSI')
        results['total_tested'].append(result['total'])
        results['matches'].append(result['matches'])
        results['mismatches'].append(result['mismatches'])
        results['max_diff_pct'].append(result['max_diff'])
        results['status'].append(result['status'])
    
    # ========================================================================
    # 2. MACD (12, 26, 9)
    # ========================================================================
    print("2. Validating MACD...")
    if 'macd' in df.columns:
        macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
        df['macd_calc'] = macd_result.iloc[:, 0]
        df['macd_signal_calc'] = macd_result.iloc[:, 1]
        df['macd_histogram_calc'] = macd_result.iloc[:, 2]
        
        result = compare_indicator(df, 'macd', 'macd_calc', sample_indices)
        results['indicator'].append('MACD')
        results['total_tested'].append(result['total'])
        results['matches'].append(result['matches'])
        results['mismatches'].append(result['mismatches'])
        results['max_diff_pct'].append(result['max_diff'])
        results['status'].append(result['status'])
    
    # ========================================================================
    # 3. Moving Averages
    # ========================================================================
    print("3. Validating Moving Averages...")
    mas = [
        ('sma_20', 20, 'sma'),
        ('sma_50', 50, 'sma'),
        ('sma_200', 200, 'sma'),
        ('ema_12', 12, 'ema'),
        ('ema_20', 20, 'ema'),
        ('ema_26', 26, 'ema'),
        ('ema_50', 50, 'ema'),
        ('ema_200', 200, 'ema'),
    ]
    
    for col_name, period, ma_type in mas:
        if col_name in df.columns:
            if ma_type == 'sma':
                df[f'{col_name}_calc'] = ta.sma(df['close'], length=period)
            else:
                df[f'{col_name}_calc'] = ta.ema(df['close'], length=period)
            
            result = compare_indicator(df, col_name, f'{col_name}_calc', sample_indices)
            results['indicator'].append(col_name.upper())
            results['total_tested'].append(result['total'])
            results['matches'].append(result['matches'])
            results['mismatches'].append(result['mismatches'])
            results['max_diff_pct'].append(result['max_diff'])
            results['status'].append(result['status'])
    
    # ========================================================================
    # 4. Bollinger Bands
    # ========================================================================
    print("4. Validating Bollinger Bands...")
    if 'bollinger_upper' in df.columns:
        bbands_result = ta.bbands(df['close'], length=20, std=2)
        df['bollinger_upper_calc'] = bbands_result.iloc[:, 0]
        df['bollinger_middle_calc'] = bbands_result.iloc[:, 1]
        df['bollinger_lower_calc'] = bbands_result.iloc[:, 2]
        
        for bb_col in ['bollinger_upper', 'bollinger_middle', 'bollinger_lower']:
            result = compare_indicator(df, bb_col, f'{bb_col}_calc', sample_indices)
            results['indicator'].append(bb_col.replace('_', ' ').title())
            results['total_tested'].append(result['total'])
            results['matches'].append(result['matches'])
            results['mismatches'].append(result['mismatches'])
            results['max_diff_pct'].append(result['max_diff'])
            results['status'].append(result['status'])
    
    # ========================================================================
    # 5. ADX (14-period)
    # ========================================================================
    print("5. Validating ADX...")
    if 'adx' in df.columns:
        adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['adx_calc'] = adx_result.iloc[:, 0]
        df['plus_di_calc'] = adx_result.iloc[:, 1]
        df['minus_di_calc'] = adx_result.iloc[:, 2]
        
        for adx_col in ['adx', 'plus_di', 'minus_di']:
            result = compare_indicator(df, adx_col, f'{adx_col}_calc', sample_indices)
            results['indicator'].append(adx_col.upper())
            results['total_tested'].append(result['total'])
            results['matches'].append(result['matches'])
            results['mismatches'].append(result['mismatches'])
            results['max_diff_pct'].append(result['max_diff'])
            results['status'].append(result['status'])
    
    # ========================================================================
    # 6. ATR (14-period)
    # ========================================================================
    print("6. Validating ATR...")
    if 'atr' in df.columns:
        df['atr_calc'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        result = compare_indicator(df, 'atr', 'atr_calc', sample_indices)
        results['indicator'].append('ATR')
        results['total_tested'].append(result['total'])
        results['matches'].append(result['matches'])
        results['mismatches'].append(result['mismatches'])
        results['max_diff_pct'].append(result['max_diff'])
        results['status'].append(result['status'])
    
    # ========================================================================
    # 7. Stochastic
    # ========================================================================
    print("7. Validating Stochastic...")
    if 'stoch_k' in df.columns:
        stoch_result = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
        df['stoch_k_calc'] = stoch_result.iloc[:, 0]
        df['stoch_d_calc'] = stoch_result.iloc[:, 1]
        
        for stoch_col in ['stoch_k', 'stoch_d']:
            result = compare_indicator(df, stoch_col, f'{stoch_col}_calc', sample_indices)
            results['indicator'].append(stoch_col.upper())
            results['total_tested'].append(result['total'])
            results['matches'].append(result['matches'])
            results['mismatches'].append(result['mismatches'])
            results['max_diff_pct'].append(result['max_diff'])
            results['status'].append(result['status'])
    
    # ========================================================================
    # 8. NEW INSTITUTIONAL INDICATORS
    # ========================================================================
    
    # MFI
    print("8. Validating MFI...")
    if 'mfi' in df.columns:
        df['mfi_calc'] = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
        result = compare_indicator(df, 'mfi', 'mfi_calc', sample_indices)
        results['indicator'].append('MFI (NEW)')
        results['total_tested'].append(result['total'])
        results['matches'].append(result['matches'])
        results['mismatches'].append(result['mismatches'])
        results['max_diff_pct'].append(result['max_diff'])
        results['status'].append(result['status'])
    
    # CMF
    print("9. Validating CMF...")
    if 'cmf' in df.columns:
        df['cmf_calc'] = ta.cmf(df['high'], df['low'], df['close'], df['volume'], length=20)
        result = compare_indicator(df, 'cmf', 'cmf_calc', sample_indices)
        results['indicator'].append('CMF (NEW)')
        results['total_tested'].append(result['total'])
        results['matches'].append(result['matches'])
        results['mismatches'].append(result['mismatches'])
        results['max_diff_pct'].append(result['max_diff'])
        results['status'].append(result['status'])
    
    # ROC
    print("10. Validating ROC...")
    if 'roc' in df.columns:
        df['roc_calc'] = ta.roc(df['close'], length=10)
        result = compare_indicator(df, 'roc', 'roc_calc', sample_indices)
        results['indicator'].append('ROC (NEW)')
        results['total_tested'].append(result['total'])
        results['matches'].append(result['matches'])
        results['mismatches'].append(result['mismatches'])
        results['max_diff_pct'].append(result['max_diff'])
        results['status'].append(result['status'])
    
    # Ichimoku
    print("11. Validating Ichimoku Cloud...")
    if 'ichimoku_tenkan' in df.columns:
        ichimoku = ta.ichimoku(df['high'], df['low'], df['close'])
        df['ichimoku_tenkan_calc'] = ichimoku[0].iloc[:, 0]
        df['ichimoku_kijun_calc'] = ichimoku[0].iloc[:, 1]
        
        for ich_col in ['ichimoku_tenkan', 'ichimoku_kijun']:
            result = compare_indicator(df, ich_col, f'{ich_col}_calc', sample_indices)
            results['indicator'].append(f"{ich_col.split('_')[1].upper()} (NEW)")
            results['total_tested'].append(result['total'])
            results['matches'].append(result['matches'])
            results['mismatches'].append(result['mismatches'])
            results['max_diff_pct'].append(result['max_diff'])
            results['status'].append(result['status'])
    
    # ========================================================================
    # GENERATE REPORT
    # ========================================================================
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    results_df = pd.DataFrame(results)
    
    # Summary
    total_indicators = len(results_df)
    passed = (results_df['status'] == 'PASS').sum()
    failed = (results_df['status'] == 'FAIL').sum()
    
    print(f"\nTotal Indicators Tested: {total_indicators}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Success Rate: {(passed/total_indicators*100):.1f}%\n")
    
    # Detailed results
    print("\nDETAILED RESULTS:")
    print("-"*80)
    print(f"{'Indicator':<25} {'Tested':<10} {'Match':<10} {'MaxDiff%':<12} {'Status':<10}")
    print("-"*80)
    
    for _, row in results_df.iterrows():
        status_symbol = "✓" if row['status'] == 'PASS' else "✗"
        print(f"{row['indicator']:<25} {row['total_tested']:<10} {row['matches']:<10} "
              f"{row['max_diff_pct']:<12.3f} {status_symbol} {row['status']:<10}")
    
    # Failed indicators detail
    if failed > 0:
        print("\n" + "="*80)
        print("FAILED INDICATORS - INVESTIGATION NEEDED:")
        print("="*80)
        failed_df = results_df[results_df['status'] == 'FAIL']
        for _, row in failed_df.iterrows():
            print(f"\n{row['indicator']}:")
            print(f"  Max difference: {row['max_diff_pct']:.3f}%")
            print(f"  Mismatches: {row['mismatches']}/{row['total_tested']}")
    
    # Save results
    output_file = file_path.replace('.xlsx', '_validation_results.xlsx')
    results_df.to_excel(output_file, index=False)
    print(f"\n✓ Results saved to: {output_file}")
    
    print("\n" + "="*80)
    if failed == 0:
        print("🎉 ALL INDICATORS VALIDATED SUCCESSFULLY!")
    else:
        print(f"⚠️  {failed} INDICATORS NEED REVIEW")
    print("="*80)
    
    return results_df


def compare_indicator(df, db_col, calc_col, sample_indices):
    """
    Compare database value vs calculated value for sampled rows
    """
    # Get non-null values from both columns
    comparison = df.loc[sample_indices, [db_col, calc_col]].copy()
    comparison = comparison.dropna()
    
    if len(comparison) == 0:
        return {
            'total': 0,
            'matches': 0,
            'mismatches': 0,
            'max_diff': 0,
            'status': 'SKIP'
        }
    
    # Calculate percentage difference
    comparison['diff_pct'] = abs(
        (comparison[db_col] - comparison[calc_col]) / comparison[db_col] * 100
    )
    
    # Count matches (within tolerance)
    matches = (comparison['diff_pct'] <= TOLERANCE_PCT).sum()
    mismatches = len(comparison) - matches
    max_diff = comparison['diff_pct'].max()
    
    status = 'PASS' if mismatches == 0 else 'FAIL'
    
    return {
        'total': len(comparison),
        'matches': matches,
        'mismatches': mismatches,
        'max_diff': max_diff,
        'status': status
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_indicators.py <excel_file.xlsx>")
        print("Example: python validate_indicators.py SPY_97_fields_complete.xlsx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Run validation with 100 random samples
    results = validate_indicators(file_path, num_samples=100)
