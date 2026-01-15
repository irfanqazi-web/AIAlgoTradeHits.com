"""
Batch ML Training for 2026 Hot Sectors
Runs walk-forward validation for all sector stocks
"""
import requests
import json
import time
from datetime import datetime

ML_SERVICE_URL = 'https://ml-training-service-1075463475276.us-central1.run.app'

# Define sectors based on 2026 Hot Sectors Analysis
SECTORS = {
    'Semiconductors': ['NVDA', 'AMD', 'MU', 'AVGO', 'LRCX', 'AMAT', 'KLAC', 'ASML', 'QCOM', 'MRVL', 'INTC', 'NXPI', 'ON', 'TXN', 'MCHP', 'SNPS', 'CDNS', 'ADI', 'SMCI'],
    'AI_Cloud': ['MSFT', 'AMZN', 'GOOGL', 'META', 'CRM', 'NOW', 'PLTR', 'PATH', 'DDOG', 'MDB', 'TEAM', 'IONQ'],
    'Defense_Aerospace': ['LMT', 'NOC', 'RTX', 'GD', 'BA', 'RKLB', 'JOBY'],
    'Cybersecurity': ['PANW', 'CRWD', 'ZS', 'FTNT'],
    'Healthcare_Biotech': ['LLY', 'VRTX', 'ISRG', 'ABT', 'UNH', 'TMO', 'REGN', 'MRNA', 'BIIB', 'CRSP'],
    'Power_Utilities': ['NEE', 'DUK', 'EXC', 'SO', 'CEG', 'ENPH', 'FSLR'],
    'Financials': ['JPM', 'BAC', 'V', 'MA', 'GS', 'MS', 'COF', 'BLK'],
    'Space_Robotics': ['RKLB', 'ISRG', 'ROK', 'HON']
}

def run_sector_validation(sector_name, symbols, test_start='2025-01-01', days=60):
    """Run walk-forward validation for a sector"""
    print(f"\n{'='*60}")
    print(f"SECTOR: {sector_name}")
    print(f"Stocks: {len(symbols)}")
    print(f"{'='*60}")

    # Split into batches of 5 for reliability
    batch_size = 5
    all_results = []

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(symbols) + batch_size - 1) // batch_size

        print(f"\nBatch {batch_num}/{total_batches}: {batch}")

        params = {
            'action': 'run',
            'symbols': ','.join(batch),
            'test_start': test_start,
            'walk_forward_days': days,
            'retrain_frequency': 'monthly',
            'features_mode': 'essential_8'
        }

        try:
            response = requests.get(ML_SERVICE_URL, params=params, timeout=3600)
            if response.status_code == 200:
                result = response.json()
                result['sector'] = sector_name
                result['batch'] = batch
                all_results.append(result)

                acc = result.get('overall_accuracy', 0)
                if acc:
                    print(f"  Run ID: {result.get('run_id', 'N/A')}")
                    print(f"  Accuracy: {acc:.1%}")
                    print(f"  Predictions: {result.get('total_predictions', 0)}")
                else:
                    print(f"  Completed but no accuracy returned")
            else:
                print(f"  Error: {response.status_code}")
                all_results.append({'sector': sector_name, 'batch': batch, 'error': response.text})
        except requests.exceptions.Timeout:
            print(f"  Timeout - batch may still be running")
            all_results.append({'sector': sector_name, 'batch': batch, 'status': 'timeout'})
        except Exception as e:
            print(f"  Error: {e}")
            all_results.append({'sector': sector_name, 'batch': batch, 'error': str(e)})

        # Small delay between batches
        time.sleep(2)

    return all_results

def main():
    print("=" * 60)
    print("2026 HOT SECTORS - ML BATCH TRAINING")
    print("=" * 60)
    print(f"Started: {datetime.now()}")

    all_sector_results = {}

    for sector, stocks in SECTORS.items():
        results = run_sector_validation(sector, stocks)
        all_sector_results[sector] = results

    # Summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE - SUMMARY")
    print("=" * 60)

    for sector, results in all_sector_results.items():
        successful = [r for r in results if 'overall_accuracy' in r and r['overall_accuracy']]
        if successful:
            avg_acc = sum(r['overall_accuracy'] for r in successful) / len(successful)
            total_preds = sum(r.get('total_predictions', 0) for r in successful)
            print(f"{sector}: {avg_acc:.1%} avg accuracy, {total_preds} predictions")
        else:
            print(f"{sector}: No results yet")

    # Save results
    with open('sector_training_results.json', 'w') as f:
        json.dump(all_sector_results, f, indent=2, default=str)

    print(f"\nResults saved to: sector_training_results.json")
    print(f"Completed: {datetime.now()}")

if __name__ == '__main__':
    main()
