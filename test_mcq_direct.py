#!/usr/bin/env python3
"""
Direct test of MCQ problem parsing and solving without Celery
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.services.parser import ParserService
from app.services.solver import SolverService

async def test_mcq_direct():
    """Test MCQ parsing and solving directly"""
    
    # Sample MCQ text from the math-2.png image
    mcq_text = """2. The figure below is made up of 20 identical small rectangles.

What percentage of the figure is shaded?

(1) 35%

(2) 20%

(3) 3%

(4) 7%"""

    print("🧪 Testing MCQ Detection and Solving Directly")
    print("=" * 50)
    print(f"📝 Input text:\n{mcq_text}")
    print("=" * 50)
    
    # Initialize services
    parser_service = ParserService()
    solver_service = SolverService()
    
    try:
        # Step 1: Parse the problem
        print("🔍 Step 1: Parsing problem...")
        parsed_problem = await parser_service.parse_problem(mcq_text)
        
        print(f"✅ Parsed successfully!")
        print(f"   Type: {parsed_problem.type}")
        print(f"   Statement: {parsed_problem.statement[:100]}...")
        print(f"   Options: {parsed_problem.options}")
        print(f"   Asks: {parsed_problem.asks}")
        print()
        
        # Step 2: Solve the problem
        print("🧮 Step 2: Solving problem...")
        solution = await solver_service.solve_problem(parsed_problem)
        
        print(f"✅ Solved successfully!")
        print(f"🎯 Final Answer: {solution.result}")
        print(f"📊 Confidence: {solution.confidence}")
        print(f"🔧 Method: {solution.method}")
        print(f"✅ Verified: {solution.verification_passed}")
        if hasattr(solution, 'reasoning'):
            print(f"💭 Reasoning: {solution.reasoning}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcq_direct())
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed!")
        sys.exit(1)
