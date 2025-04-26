#!/usr/bin/env python3

import sys
import math
import statistics
import argparse

def mean(d):
    return sum(d) * 1.0 / len(d)

def deviation(d):
    m = mean(d)
    return math.sqrt(sum((x-m)**2 for x in d) * 1.0 / len(d))

def format_table(headers, rows, fmt='grid'):
    """
    Create a formatted table without external dependencies
    """
    if fmt == 'csv':
        result = ','.join(headers) + '\n'
        for row in rows:
            result += ','.join(str(cell) for cell in row) + '\n'
        return result
    
    elif fmt == 'latex':
        # Create LaTeX table
        col_spec = 'l' + 'r' * (len(headers) - 1)
        result = "\\begin{tabular}{" + col_spec + "}\n"
        result += "\\hline\n"
        result += " & ".join(headers) + " \\\\\n"
        result += "\\hline\n"
        
        for row in rows:
            result += " & ".join(str(cell) for cell in row) + " \\\\\n"
        
        result += "\\hline\n"
        result += "\\end{tabular}"
        return result
    
    # Default grid format
    # Calculate column widths
    col_widths = [max(len(h), 10) for h in headers]  # Minimum width of 10
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Create the header
    header_fmt = " | ".join(f"{headers[i]:{col_widths[i]}}" for i in range(len(headers)))
    separator = "-+-".join("-" * width for width in col_widths)
    
    # Build the table
    result = header_fmt + '\n' + separator + '\n'
    
    # Add the rows
    for row in rows:
        row_fmt = " | ".join(f"{str(row[i]):{col_widths[i]}}" for i in range(len(row)))
        result += row_fmt + '\n'
    
    return result

def parse_arguments():
    parser = argparse.ArgumentParser(description='Analyze benchmark results in a nice table format')
    parser.add_argument('--format', default='grid', choices=['grid', 'csv', 'latex'],
                        help='Table format (default: grid)')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # If using LaTeX format, always include package declarations
    if args.format == 'latex':
        print("% Include these packages in your LaTeX document")
        print("\\usepackage{booktabs}")
        print("\\usepackage{array}")
        print("\\usepackage{siunitx}")
        print()
    
    keys = set()
    validate = {}
    action = {}
    torsion = {}
    mults = {}
    sqs = {}
    adds = {}
    num = 0

    # Parse benchmark data from stdin
    for line in sys.stdin:
        line = line.split()
        if len(line) < 11: continue
        if line[3] != 'mulsq': continue
        if line[5] != 'sq': continue
        if line[7] != 'addsub': continue
        if line[9] != 'cycles': continue

        if line[2] == 'validate':
            target = validate
        elif line[2] == 'action':
            target = action
        elif line[2] == 'torsionpoint':
            target = torsion
        elif line[2] == 'mults':
            target = mults
        elif line[2] == 'sqs':
            target = sqs
        elif line[2] == 'adds':
            target = adds
        else:
            continue

        mul = int(line[4])
        sq = int(line[6])
        addsub = int(line[8])
        Mcyc = 0.000001 * int(line[10])
        mulsq = mul + sq
        combo185 = mul + 0.8 * sq + 0.05 * addsub

        keys.add(int(line[1]))
        for k in [int(line[1]), 'total']:
            for name, value in (
                ('Mcyc', Mcyc),
                ('mulsq', mulsq),
                ('sq', sq),
                ('addsub', addsub),
                ('mul', mul),
                ('combo185', combo185),
            ):
                if (k, name) not in target:
                    target[k, name] = []
                target[k, name] += [value]

        num += 1

    # Always display only the total
    display_keys = ['total']
    
    # Format numbers properly based on their type
    def format_value(name, value):
        if name == 'Mcyc':
            return f"{value:.5f}"
        else:
            return f"{value:.0f}"
    
    # Prepare LaTeX full document if needed
    if args.format == 'latex':
        print("% You can copy and paste these tables into your LaTeX document")
        print("% or use them in a standalone document like this:")
        print("% ------------------------------------------------------")
        print("\\documentclass{article}")
        print("\\usepackage{booktabs}")
        print("\\usepackage{array}")
        print("\\usepackage{siunitx}")
        print("\\begin{document}")
        print()

    # Print results for each operation type
    for targetname, target in [
        ('validate', validate),
        ('action', action),
        ('torsionpoint', torsion),
        ('mults', mults),
        ('sqs', sqs),
        ('adds', adds),
    ]:
        if target == {}:
            continue
        
        if args.format != 'latex':
            print(f"\n=== {targetname.upper()} ===")
            print(f"Number of experiments: {len(target.get(('total', 'Mcyc'), []))}")
        else:
            print(f"% {targetname.upper()} - {len(target.get(('total', 'Mcyc'), []))} experiments")
        
        for k in display_keys:
            if (k, 'Mcyc') not in target:
                continue
            
            # For LaTeX, add a caption and label
            if args.format == 'latex':
                print("\\begin{table}[htbp]")
                print("  \\centering")
                print(f"  \\caption{{{targetname.title()} Benchmark Results}}")
                print(f"  \\label{{tab:{targetname.lower()}_benchmarks}}")
            
            # Create table headers and rows
            headers = ["Metric", "Median", "Mean", "Std Dev", "Min", "Max"]
            rows = []
            
            # Order metrics by importance
            metrics_order = ['Mcyc', 'mulsq', 'mul', 'sq', 'addsub', 'combo185']
            
            for name in metrics_order:
                if (k, name) not in target:
                    continue
                
                x = target[k, name]
                row = [
                    name,
                    format_value(name, statistics.median(x)),
                    format_value(name, mean(x)),
                    format_value(name, deviation(x)),
                    format_value(name, min(x)),
                    format_value(name, max(x))
                ]
                rows.append(row)
            
            # Print the formatted table
            table_output = format_table(headers, rows, args.format)
            if args.format == 'latex':
                # Indent the table for better readability in the LaTeX source
                indented_table = "  " + table_output.replace("\n", "\n  ")
                print(indented_table)
                print("\\end{table}")
                print()
            else:
                print(table_output)
    
    # Close LaTeX document if needed
    if args.format == 'latex':
        print("\\end{document}")
        print("% ------------------------------------------------------")

if __name__ == "__main__":
    main()
