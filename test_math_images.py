#!/usr/bin/env python3
"""
Generic test script for math images
Usage: python test_math_images.py "math-3.png"
       python test_math_images.py "path/to/image.png"
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_math_image(image_path: str, image_name: str):
    """Test processing a single math image"""
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 TESTING: {image_name}")
        logger.info(f"📁 Path: {image_path}")
        logger.info(f"{'='*60}")
        
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"❌ File not found: {image_path}")
            return None
        
        # Get file size
        file_size = os.path.getsize(image_path)
        logger.info(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Read image content
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        logger.info(f"✅ Image loaded successfully")
        
        # Import services
        from app.services.ocr import ocr_service
        from app.services.parser import parser_service
        from app.services.solver import solver_service
        
        # Step 1: OCR Processing
        logger.info("🔍 Step 1: OCR Processing...")
        try:
            ocr_result = await ocr_service.process_image(image_content)
            logger.info(f"✅ OCR completed - Confidence: {ocr_result.confidence:.2f}")
            logger.info(f"📝 Extracted text: {ocr_result.text[:200]}...")
            if ocr_result.latex:
                logger.info(f"🔢 LaTeX: {ocr_result.latex[:100]}...")
        except Exception as e:
            logger.error(f"❌ OCR failed: {e}")
            return {"error": f"OCR failed: {e}", "stage": "ocr"}
        
        # Step 2: Problem Parsing
        logger.info("🧠 Step 2: Problem Parsing...")
        try:
            parsed_problem = await parser_service.parse_problem(
                ocr_result.text, 
                ocr_result.latex,
                image_content=image_content
            )
            logger.info(f"✅ Parsing completed - Type: {parsed_problem.type}")
            logger.info(f"❓ Statement: {parsed_problem.statement[:150]}...")
            if parsed_problem.options:
                logger.info(f"📋 Options: {len(parsed_problem.options)} choices")
                for i, opt in enumerate(parsed_problem.options[:3]):  # Show first 3 options
                    logger.info(f"   {chr(65+i)}) {opt[:50]}...")
        except Exception as e:
            logger.error(f"❌ Parsing failed: {e}")
            return {"error": f"Parsing failed: {e}", "stage": "parsing", "ocr_result": ocr_result.model_dump()}
        
        # Step 3: Math Solving
        logger.info("🧮 Step 3: Math Solving...")
        try:
            solution = await solver_service.solve_problem(parsed_problem)
            logger.info(f"✅ Solving completed - Confidence: {solution.confidence:.2f}")
            logger.info(f"💡 Result: {solution.result}")
            logger.info(f"📝 Method: {solution.method}")
            if solution.steps:
                logger.info(f"📖 Steps: {len(solution.steps)} steps available")
        except Exception as e:
            logger.error(f"❌ Solving failed: {e}")
            return {"error": f"Solving failed: {e}", "stage": "solving", "parsed_problem": parsed_problem.model_dump()}
        
        # Compile results
        result = {
            "image": image_name,
            "success": True,
            "ocr": {
                "text": ocr_result.text,
                "latex": ocr_result.latex,
                "confidence": ocr_result.confidence
            },
            "parsed": {
                "type": parsed_problem.type,
                "statement": parsed_problem.statement,
                "options": parsed_problem.options,
                "asks": parsed_problem.asks
            },
            "solution": {
                "result": solution.result,
                "method": solution.method,
                "steps": [step.model_dump() for step in solution.steps],
                "confidence": solution.confidence,
                "verification_passed": solution.verification_passed
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🎉 SUCCESS: {image_name} processed completely!")
        return result
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR processing {image_name}: {e}")
        return {"error": str(e), "stage": "fatal", "image": image_name}

async def run_single_test(image_path: str):
    """Run test for a single image"""
    logger.info("🚀 Starting Math Image Test")
    logger.info(f"⏰ Start time: {datetime.now()}")
    
    # Get image name from path
    image_name = os.path.basename(image_path)
    
    # Test the image
    result = await test_math_image(image_path, image_name)
    
    # Display results
    logger.info(f"\n{'='*80}")
    logger.info("📋 TEST RESULT")
    logger.info(f"{'='*80}")
    
    if result:
        if result.get('success', False):
            logger.info(f"✅ SUCCESS: {image_name}")
            solution_result = result['solution']['result']
            if isinstance(solution_result, dict) and 'correct_answer' in solution_result:
                logger.info(f"    Answer: {solution_result['correct_answer']}")
            else:
                logger.info(f"    Result: {solution_result}")
            logger.info(f"    Method: {result['solution']['method']}")
            logger.info(f"    Confidence: {result['solution']['confidence']:.2f}")
        else:
            logger.info(f"❌ FAILED: {image_name} ({result.get('stage', 'unknown')})")
            logger.info(f"    Error: {result.get('error', 'Unknown error')}")
    else:
        logger.info(f"❌ NO RESULT: {image_name}")
    
    # Save results
    results_file = f"test_result_{image_name.replace('.', '_')}.json"
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info(f"\n💾 Detailed results saved to: {results_file}")
    logger.info(f"⏰ End time: {datetime.now()}")
    logger.info("🏁 Test completed!")
    
    return result

async def run_all_tests():
    """Run tests for all math images (fallback for backward compatibility)"""
    logger.info("🚀 Starting Math Images Test Suite")
    logger.info(f"⏰ Start time: {datetime.now()}")
    
    # Define image files to test
    image_files = [
        "math-2.png",
        "math-3.png", 
        "math-4.png",
        "math-5.png",
        "math-6.png"
    ]
    
    results = []
    
    for image_file in image_files:
        image_path = os.path.join(".", image_file)
        result = await test_math_image(image_path, image_file)
        results.append(result)
        
        # Brief pause between tests
        await asyncio.sleep(1)
    
    # Generate summary
    logger.info(f"\n{'='*80}")
    logger.info("📋 TEST SUMMARY")
    logger.info(f"{'='*80}")
    
    successful = sum(1 for r in results if r and r.get('success', False))
    total = len(results)
    
    logger.info(f"✅ Successful: {successful}/{total}")
    logger.info(f"❌ Failed: {total - successful}/{total}")
    
    for i, result in enumerate(results):
        if result:
            status = "✅ SUCCESS" if result.get('success', False) else f"❌ FAILED ({result.get('stage', 'unknown')})"
            logger.info(f"  {image_files[i]}: {status}")
            if result.get('success', False):
                solution_result = result['solution']['result']
                if isinstance(solution_result, dict) and 'correct_answer' in solution_result:
                    logger.info(f"    Answer: {solution_result['correct_answer']}")
                else:
                    logger.info(f"    Result: {solution_result}")
                logger.info(f"    Method: {result['solution']['method']}")
        else:
            logger.info(f"  {image_files[i]}: ❌ NO RESULT")
    
    # Save detailed results
    results_file = "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n💾 Detailed results saved to: {results_file}")
    logger.info(f"⏰ End time: {datetime.now()}")
    logger.info("🏁 Test suite completed!")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single image test mode
        image_path = sys.argv[1]
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"❌ Error: File '{image_path}' not found!")
            print("\n💡 Usage:")
            print("  python test_math_images.py \"math-3.png\"")
            print("  python test_math_images.py \"path/to/image.png\"")
            print("  python test_math_images.py  # Run all tests")
            sys.exit(1)
        
        # Run single test
        asyncio.run(run_single_test(image_path))
    else:
        # Multiple images test mode (default)
        print("💡 No image specified. Running all tests...")
        print("   To test a single image: python test_math_images.py \"math-3.png\"")
        asyncio.run(run_all_tests())
