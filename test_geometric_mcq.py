#!/usr/bin/env python3
"""
Direct test of geometric MCQ solving with detailed logging
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.services.solver import SolverService
from app.models import ParsedProblem, ProblemType

async def test_geometric_mcq():
    """Test geometric MCQ solving directly"""
    
    print("🧪 Testing Geometric MCQ Solving Directly")
    print("=" * 50)
    
    # Create the triangle geometry problem
    problem = ParsedProblem(
        type=ProblemType.MCQ,
        statement="Given that AD is the base of triangle ABD. Identify the height that is related to the base AD.",
        options=["A) AB", "B) AC", "C) BD", "D) BE"],
        asks=["identify_related_height"],
        variables=[]
    )
    
    print(f"📝 Problem Statement: {problem.statement}")
    print(f"📝 Options: {problem.options}")
    print()
    
    # Initialize solver
    solver_service = SolverService()
    
    try:
        # Solve the problem
        print("🧮 Solving geometric MCQ...")
        solution = await solver_service._solve_mcq(problem)
        
        print(f"✅ Solved successfully!")
        print(f"🎯 Final Answer: {solution.result.get('correct_answer')}")
        print(f"📊 Confidence: {solution.confidence}")
        print(f"🔧 Method: {solution.method}")
        print(f"✅ Verified: {solution.verification_passed}")
        print()
        
        # Show detailed reasoning
        result = solution.result
        if isinstance(result, dict) and 'reasoning' in result:
            print(f"💭 Detailed Reasoning:")
            print(result['reasoning'])
        
        # Show steps
        if solution.steps:
            print(f"\n📝 Solution Steps:")
            for step in solution.steps:
                print(f"  Step {step.step_number}: {step.description}")
                if step.explanation:
                    print(f"    → {step.explanation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_geometric_mcq())
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
