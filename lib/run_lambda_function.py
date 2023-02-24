#!/usr/bin/env python3
import argparse
import lambda_function
import json

parser = argparse.ArgumentParser(description='Run Lambda handler locally')
parser.add_argument(
    '--event',
    type=str,
    dest='event',
    required=True,
    help='TRE output event to be processed'
)
args = parser.parse_args()
event_dict = json.loads(args.event)
print(f'run_lambda_function: calling lambda...')
result = lambda_function.lambda_handler(event_dict, None)
print(f'run_lambda_function: lambda call complete')
print(f'--- result start {"-" * 63}\n{result}\n--- result end {"-" * 65}')
