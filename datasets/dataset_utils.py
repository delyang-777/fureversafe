#!/usr/bin/env python3
"""
FurEverSafe Dataset Utility Script
Convert and manage training datasets for LLM fine-tuning
"""

import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict
import random

class DatasetConverter:
    """Convert between different dataset formats"""
    
    @staticmethod
    def jsonl_to_csv(input_file: str, output_file: str):
        """Convert JSONL to CSV format"""
        print(f"Converting {input_file} to CSV...")
        
        with open(input_file, 'r') as f:
            with open(output_file, 'w', newline='', encoding='utf-8') as out:
                writer = csv.writer(out)
                writer.writerow(['instruction', 'input', 'output'])
                for line in f:
                    obj = json.loads(line)
                    writer.writerow([
                        obj.get('instruction', ''),
                        obj.get('input', ''),
                        obj.get('output', '')
                    ])
        
        print(f"✓ Converted to {output_file}")
    
    @staticmethod
    def jsonl_to_gpt_format(input_file: str, output_file: str):
        """Convert to OpenAI GPT fine-tuning format"""
        print(f"Converting {input_file} to GPT format...")
        
        output = []
        with open(input_file, 'r') as f:
            for line in f:
                obj = json.loads(line)
                output.append({
                    "messages": [
                        {"role": "system", "content": obj.get('instruction', '')},
                        {"role": "user", "content": obj.get('input', '')},
                        {"role": "assistant", "content": obj.get('output', '')}
                    ]
                })
        
        with open(output_file, 'w') as f:
            for obj in output:
                f.write(json.dumps(obj) + '\n')
        
        print(f"✓ Converted to {output_file}")
    
    @staticmethod
    def jsonl_to_alpaca_format(input_file: str, output_file: str):
        """Convert to Alpaca instruction format"""
        print(f"Converting {input_file} to Alpaca format...")
        
        output = []
        with open(input_file, 'r') as f:
            for line in f:
                obj = json.loads(line)
                output.append({
                    "instruction": obj.get('input', ''),
                    "input": "",
                    "output": obj.get('output', '')
                })
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Converted to {output_file}")
    
    @staticmethod
    def csv_to_jsonl(input_file: str, output_file: str):
        """Convert CSV to JSONL format"""
        print(f"Converting {input_file} to JSONL...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with open(output_file, 'w') as out:
                for row in reader:
                    obj = {
                        "instruction": row.get('instruction', ''),
                        "input": row.get('input', ''),
                        "output": row.get('output', '')
                    }
                    out.write(json.dumps(obj) + '\n')
        
        print(f"✓ Converted to {output_file}")


class DatasetAnalyzer:
    """Analyze dataset statistics"""
    
    @staticmethod
    def analyze_jsonl(input_file: str):
        """Analyze JSONL dataset"""
        print(f"\n📊 Analyzing {input_file}...\n")
        
        stats = {
            'total_examples': 0,
            'avg_instruction_length': 0,
            'avg_input_length': 0,
            'avg_output_length': 0,
            'total_instruction_chars': 0,
            'total_input_chars': 0,
            'total_output_chars': 0,
            'categories': {}
        }
        
        with open(input_file, 'r') as f:
            for line in f:
                obj = json.loads(line)
                stats['total_examples'] += 1
                stats['total_instruction_chars'] += len(obj.get('instruction', ''))
                stats['total_input_chars'] += len(obj.get('input', ''))
                stats['total_output_chars'] += len(obj.get('output', ''))
                
                # Extract category from first word of input
                first_word = obj.get('input', '').split()[0] if obj.get('input') else 'unknown'
                stats['categories'][first_word] = stats['categories'].get(first_word, 0) + 1
        
        # Calculate averages
        if stats['total_examples'] > 0:
            stats['avg_instruction_length'] = stats['total_instruction_chars'] / stats['total_examples']
            stats['avg_input_length'] = stats['total_input_chars'] / stats['total_examples']
            stats['avg_output_length'] = stats['total_output_chars'] / stats['total_examples']
        
        # Print results
        print(f"Total Examples: {stats['total_examples']}")
        print(f"Average Instruction Length: {stats['avg_instruction_length']:.0f} chars")
        print(f"Average Input Length: {stats['avg_input_length']:.0f} chars")
        print(f"Average Output Length: {stats['avg_output_length']:.0f} chars")
        print(f"Total Dataset Size: {(stats['total_instruction_chars'] + stats['total_input_chars'] + stats['total_output_chars']) / 1024:.1f} KB")
        
        print(f"\nTop Categories:")
        for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {cat}: {count}")
        
        return stats


class DatasetSplitter:
    """Split dataset into train/validation/test sets"""
    
    @staticmethod
    def split_dataset(input_file: str, train_ratio: float = 0.7, val_ratio: float = 0.15, 
                     test_ratio: float = 0.15, output_dir: str = './splits'):
        """Split dataset into train/val/test"""
        print(f"\nSplitting {input_file}...")
        print(f"Train: {train_ratio*100}% | Val: {val_ratio*100}% | Test: {test_ratio*100}%\n")
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Load all examples
        examples = []
        with open(input_file, 'r') as f:
            for line in f:
                examples.append(json.loads(line))
        
        # Shuffle
        random.shuffle(examples)
        
        # Calculate split indices
        total = len(examples)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        train_set = examples[:train_end]
        val_set = examples[train_end:val_end]
        test_set = examples[val_end:]
        
        # Write files
        def write_set(data, filename):
            path = Path(output_dir) / filename
            with open(path, 'w') as f:
                for obj in data:
                    f.write(json.dumps(obj) + '\n')
            print(f"✓ {filename}: {len(data)} examples ({len(data)/total*100:.1f}%)")
        
        write_set(train_set, 'train.jsonl')
        write_set(val_set, 'val.jsonl')
        write_set(test_set, 'test.jsonl')
        
        print(f"\n✓ Split complete! Output in {output_dir}/")
        return train_set, val_set, test_set


class DatasetValidator:
    """Validate dataset quality"""
    
    @staticmethod
    def validate_jsonl(input_file: str):
        """Validate JSONL dataset"""
        print(f"\n✓ Validating {input_file}...\n")
        
        errors = []
        warnings = []
        
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    obj = json.loads(line)
                    
                    # Check required fields
                    if 'instruction' not in obj:
                        errors.append(f"Line {line_num}: Missing 'instruction' field")
                    if 'input' not in obj:
                        errors.append(f"Line {line_num}: Missing 'input' field")
                    if 'output' not in obj:
                        errors.append(f"Line {line_num}: Missing 'output' field")
                    
                    # Check for empty fields
                    if not obj.get('instruction', '').strip():
                        warnings.append(f"Line {line_num}: Empty instruction")
                    if not obj.get('input', '').strip():
                        warnings.append(f"Line {line_num}: Empty input")
                    if not obj.get('output', '').strip():
                        warnings.append(f"Line {line_num}: Empty output")
                    
                    # Check length
                    if len(obj.get('output', '')) < 20:
                        warnings.append(f"Line {line_num}: Very short output ({len(obj['output'])} chars)")
                    if len(obj.get('output', '')) > 3000:
                        warnings.append(f"Line {line_num}: Very long output ({len(obj['output'])} chars)")
                
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
        
        # Print results
        print(f"✓ Validation Results:")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        
        if errors:
            print(f"\n❌ Errors:")
            for error in errors[:10]:
                print(f"  {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings[:10]:
                print(f"  {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more warnings")
        
        return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description='FurEverSafe Dataset Utility')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert dataset format')
    convert_parser.add_argument('input', help='Input file')
    convert_parser.add_argument('--to', choices=['csv', 'gpt', 'alpaca'], required=True, help='Output format')
    convert_parser.add_argument('--output', '-o', help='Output file (auto-generated if not specified)')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze dataset')
    analyze_parser.add_argument('input', help='Input JSONL file')
    
    # Split command
    split_parser = subparsers.add_parser('split', help='Split dataset')
    split_parser.add_argument('input', help='Input JSONL file')
    split_parser.add_argument('--train', type=float, default=0.7, help='Train ratio (default: 0.7)')
    split_parser.add_argument('--val', type=float, default=0.15, help='Validation ratio (default: 0.15)')
    split_parser.add_argument('--test', type=float, default=0.15, help='Test ratio (default: 0.15)')
    split_parser.add_argument('--output-dir', '-o', default='./splits', help='Output directory')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate dataset')
    validate_parser.add_argument('input', help='Input JSONL file')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        output_file = args.output or f"{Path(args.input).stem}.{args.to}"
        
        if args.to == 'csv':
            DatasetConverter.jsonl_to_csv(args.input, output_file)
        elif args.to == 'gpt':
            DatasetConverter.jsonl_to_gpt_format(args.input, output_file)
        elif args.to == 'alpaca':
            DatasetConverter.jsonl_to_alpaca_format(args.input, output_file)
    
    elif args.command == 'analyze':
        DatasetAnalyzer.analyze_jsonl(args.input)
    
    elif args.command == 'split':
        DatasetSplitter.split_dataset(args.input, args.train, args.val, args.test, args.output_dir)
    
    elif args.command == 'validate':
        DatasetValidator.validate_jsonl(args.input)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
