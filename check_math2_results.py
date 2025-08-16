#!/usr/bin/env python3
import requests
import json

headers = {'X-API-Key': 'math-api-key-2025'}
response = requests.get('http://localhost:8000/v1/problems/gq0jnKdgXl9HuX3fMUYT', headers=headers)

if response.status_code == 200:
    data = response.json()
    print('🔍 MATH-2.PNG COMPLETE ANALYSIS')
    print('=' * 60)
    
    # OCR Result
    ocr = data.get('ocr_result', {})
    print('📝 MISTRAL OCR EXTRACTED TEXT:')
    print(ocr.get('text', 'none'))
    print()
    
    # Parsed Problem  
    parsed = data.get('parsed_problem', {})
    print('🤖 OPENAI PARSING:')
    print(f'Problem Type: {parsed.get("type", "unknown")}')
    print(f'Statement: {parsed.get("statement", "none")}')
    print(f'What it asks: {parsed.get("asks", [])}')
    print(f'Options found: {parsed.get("options", [])}')
    print()
    
    # Solution
    solution = data.get('solution', {})
    print('💡 SOLVER RESULT:')
    print(f'Method used: {solution.get("method", "unknown")}')
    print(f'Confidence: {solution.get("confidence", 0)}')
    print(f'Result: {solution.get("result", "none")}')
    print(f'Steps taken: {len(solution.get("steps", []))}')
    
    steps = solution.get('steps', [])
    if steps:
        print('\n📋 SOLUTION STEPS:')
        for step in steps:
            print(f'Step {step.get("step_number", "?")}: {step.get("description", "none")}')
            if step.get('explanation'):
                print(f'  → {step.get("explanation", "none")}')
            print()
    
else:
    print(f'Error: {response.status_code}')
