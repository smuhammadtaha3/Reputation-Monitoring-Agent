"""
Convert text files (__label__N text format) to JSON lines format
Compatible with Yelp dataset format expected by the EDA code
Uses efficient chunked writing for large files
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import random
import sys

def convert_txt_to_json(input_file, output_file, chunk_size=10000):
    """Convert text file to JSON lines format with efficient buffering"""
    
    print(f"Converting {input_file} → {output_file}", flush=True)
    sys.stdout.flush()
    
    count = 0
    start_date = datetime(2020, 1, 1)
    buffer = []
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore', buffering=8192) as infile:
            with open(output_file, 'w', encoding='utf-8', buffering=65536) as outfile:
                
                for line in infile:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse __label__N text format
                    if line.startswith('__label__'):
                        try:
                            parts = line.split(' ', 1)
                            label = parts[0].replace('__label__', '')
                            text = parts[1] if len(parts) > 1 else ""
                            
                            # Map label to stars (1,2 → scale to 1-5)
                            try:
                                label_num = int(label)
                                if label_num == 1:
                                    stars = random.randint(1, 2)
                                elif label_num == 2:
                                    stars = random.randint(4, 5)
                                else:
                                    stars = 3
                            except:
                                stars = 3
                            
                            # Generate random date
                            random_days = random.randint(0, 365*3)
                            review_date = start_date + timedelta(days=random_days)
                            
                            # Create JSON object
                            record = {
                                'text': text,
                                'stars': stars,
                                'date': review_date.strftime('%Y-%m-%d'),
                                'useful': random.randint(0, 50),
                                'funny': random.randint(0, 30),
                                'cool': random.randint(0, 20)
                            }
                            
                            buffer.append(json.dumps(record))
                            count += 1
                            
                            # Write buffer to file periodically
                            if len(buffer) >= chunk_size:
                                outfile.write('\n'.join(buffer) + '\n')
                                outfile.flush()
                                buffer = []
                                print(f"  ✓ Processed {count:,} records...", flush=True)
                                sys.stdout.flush()
                        
                        except Exception as e:
                            print(f"  ⚠ Error processing line: {e}", file=sys.stderr)
                            continue
                
                # Write remaining buffer
                if buffer:
                    outfile.write('\n'.join(buffer) + '\n')
                    outfile.flush()
        
        print(f"✅ Completed! {count:,} records saved to {output_file}\n", flush=True)
        sys.stdout.flush()
        return count
    
    except Exception as e:
        print(f"❌ Error during conversion: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise

if __name__ == '__main__':
    # Set paths
    base_path = Path(__file__).parent / 'data' / 'archive'
    
    files_to_convert = [
        ('test.txt', 'test.json'),
        ('train.txt', 'train.json')
    ]
    
    total_records = 0
    for input_name, output_name in files_to_convert:
        input_file = base_path / input_name
        output_file = base_path / output_name
        
        if input_file.exists():
            records = convert_txt_to_json(str(input_file), str(output_file))
            total_records += records
        else:
            print(f"⚠️  File not found: {input_file}")
    
    print(f"=" * 50)
    print(f"Total records converted: {total_records:,}")
    print(f"Files ready to use with your EDA code! 🎉")
