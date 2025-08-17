from openai import OpenAI
import json
import logging
import base64
from typing import Optional
from config.settings import settings
from app.models import ParsedProblem, ProblemType

logger = logging.getLogger(__name__)


class ParserService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-5"  # Use gpt-5 for reasoning
        self.confidence_threshold = 0.7  # Threshold for using image fallback
    
    async def parse_problem(self, ocr_text: str, latex: Optional[str] = None, image_content: Optional[bytes] = None, image_url: Optional[str] = None) -> ParsedProblem:
        """
        Parse OCR output into structured problem format using LLM
        Always sends both OCR text and image to OpenAI in a single call for best accuracy
        """
        try:
            # If we have image data, use the combined text + vision approach
            if image_content or image_url:
                logger.info("🤖 Using OpenAI vision model with OCR text + image...")
                return await self._parse_with_combined_input(ocr_text, image_content, image_url, latex)
            else:
                # Fallback to text-only if no image available
                logger.info("🤖 Using OpenAI text-only parsing (no image available)...")
                return await self._parse_text_only(ocr_text, latex)
            
        except Exception as e:
            logger.error(f"Problem parsing failed: {e}")
            
            # Return a basic fallback structure
            return ParsedProblem(
                type=ProblemType.OTHER,
                statement=ocr_text,
                asks=["solve"],
                options=[],
                variables=[]
            )
    
    async def _parse_with_combined_input(self, ocr_text: str, image_content: Optional[bytes] = None, image_url: Optional[str] = None, latex: Optional[str] = None) -> ParsedProblem:
        """
        Parse problem using both OCR text and image in a single OpenAI call
        This is the main parsing method that combines text and visual analysis
        """
        try:
            logger.info("🔍 Using OpenAI vision model with combined OCR text + image...")
            
            # Create combined prompt that references both text and image
            combined_prompt = self._create_combined_parsing_prompt(ocr_text, latex)
            
            # Log the prompt being sent
            logger.info("📋 PROMPT BEING SENT TO OPENAI:")
            logger.info("=" * 50)
            logger.info(combined_prompt)
            logger.info("=" * 50)
            
            # Prepare image content for the request
            image_content_for_request = None
            
            if image_content:
                # Convert image bytes to base64
                image_b64 = base64.b64encode(image_content).decode()
                image_content_for_request = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                }
                logger.info("📡 Using base64 encoded image content with OCR text...")
            elif image_url and not image_url.startswith("http://localhost"):
                # Use the provided image URL only if it's not localhost
                image_content_for_request = {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
                logger.info(f"📡 Using external image URL with OCR text: {image_url[:50]}...")
            else:
                # If we only have a localhost URL, we can't use it with OpenAI
                if image_url and image_url.startswith("http://localhost"):
                    logger.warning("⚠️ Localhost image URL detected, but no image content provided. Falling back to text-only parsing.")
                    return await self._parse_text_only(ocr_text, latex)
                raise ValueError("No usable image content provided")
            
            # Make the combined vision + text request
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are Reasoner — a calm, precise, helpful assistant specializing in mathematics problem parsing with vision capabilities. You analyze both extracted OCR text and original images to parse problems into structured JSON format. Internally reason step-by-step to reach correct conclusions, but DO NOT reveal internal chain-of-thought, private deliberation, or stream-of-consciousness. Always output a concise, user-safe result in the exact format described."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": combined_prompt
                            },
                            image_content_for_request
                        ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                verbosity="medium",
                reasoning_effort="medium"
            )
            
            # Parse the response from standard chat completions API
            content = response.choices[0].message.content
            logger.info(f"📋 OpenAI combined response received: {len(content)} characters")
            
            parsed_data = json.loads(content)
            return ParsedProblem(**parsed_data)
            
        except Exception as e:
            logger.error(f"Combined parsing failed: {e}")
            # Fallback to text-only parsing
            logger.info("🔄 Falling back to text-only parsing...")
            return await self._parse_text_only(ocr_text, latex)

    async def _parse_text_only(self, ocr_text: str, latex: Optional[str] = None) -> ParsedProblem:
        """
        Parse problem using only text (fallback method)
        """
        try:
            logger.info("🤖 Using OpenAI text-only parsing...")
            prompt = self._create_parsing_prompt(ocr_text, latex)
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are Reasoner — a calm, precise, helpful assistant specializing in mathematics problem parsing. You parse given text into structured JSON format. Internally reason step-by-step to reach correct conclusions, but DO NOT reveal internal chain-of-thought, private deliberation, or stream-of-consciousness. Always output a concise, user-safe result in the exact format described."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                verbosity="medium",
                reasoning_effort="medium"
            )
            
            # Parse the response from standard chat completions API
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            return ParsedProblem(**parsed_data)
            
        except Exception as e:
            logger.error(f"Text-only parsing failed: {e}")
            raise
        """
        Enhanced image parsing that supports both image content and URLs
        This implements the fallback mechanism for low confidence responses
        """
        try:
            logger.info("🔍 Using OpenAI vision model for enhanced parsing...")
            
            # Create vision prompt
            vision_prompt = self._create_vision_parsing_prompt(ocr_text, latex)
            
            # Prepare image content for the request
            image_content_for_request = None
            
            if image_content:
                # Convert image bytes to base64
                image_b64 = base64.b64encode(image_content).decode()
                image_content_for_request = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                }
                logger.info("📡 Using base64 encoded image content...")
            elif image_url and not image_url.startswith("http://localhost"):
                # Use the provided image URL only if it's not localhost
                image_content_for_request = {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
                logger.info(f"📡 Using external image URL: {image_url[:50]}...")
            else:
                # If we only have a localhost URL, we can't use it with OpenAI
                if image_url and image_url.startswith("http://localhost"):
                    logger.warning("⚠️ Localhost image URL detected, but no image content provided. OpenAI cannot access localhost URLs.")
                raise ValueError("No usable image content provided (localhost URLs not supported by OpenAI)")
            
            # Make the vision request with either URL or base64 content
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are Reasoner — a calm, precise, helpful assistant specializing in mathematics problem parsing with vision capabilities. You analyze both extracted text and original images to parse problems into structured JSON format. Internally reason step-by-step to reach correct conclusions, but DO NOT reveal internal chain-of-thought, private deliberation, or stream-of-consciousness. Always output a concise, user-safe result in the exact format described."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": vision_prompt
                            },
                            image_content_for_request
                        ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                verbosity="medium",
                reasoning_effort="medium"
            )
            
            logger.info("✅ OpenAI vision parsing successful!")
            
            # Parse the response from standard chat completions API
            content = response.choices[0].message.content
            logger.info(f"🔍 OpenAI vision raw response: {content[:200]}...")
            
            # Clean and parse JSON
            try:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON object found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse JSON from vision response: {e}")
                logger.error(f"Raw response: {content}")
                raise
            
            # Remove confidence field if present
            parsed_data.pop('confidence', None)
            
            logger.info("✅ OpenAI vision parsing successful!")
            return ParsedProblem(**parsed_data)
            
        except Exception as e:
            logger.error(f"Enhanced vision parsing failed: {e}")
            raise
    
    def _create_combined_parsing_prompt(self, ocr_text: str, latex: Optional[str] = None) -> str:
        """Create a prompt for combined OCR text + image analysis"""
        prompt = f"""
I have extracted text from a mathematical problem image using OCR, and I'm also providing you with the original image. Please analyze both to parse this problem accurately.

OCR Extracted Text:
{ocr_text}
"""
        
        if latex:
            prompt += f"""
LaTeX (if available): {latex}
"""
        
        prompt += """
Please examine BOTH the OCR text and the original image to:
1. Verify and correct any OCR errors by looking at the actual image
2. Identify mathematical symbols, diagrams, or visual elements that OCR might have missed
3. Understand the complete context of the problem including any visual components
4. Parse the problem into the structured format below

IMPORTANT: Return ONLY a valid JSON object with this exact structure:
{
    "type": "equation|system|integral|derivative|word_problem|mcq|geometry|graph_analysis|other",
    "statement": "The complete and corrected problem statement incorporating both text and visual elements",
    "asks": ["solve_for:x", "simplify", "compute_value", "find_derivative", "analyze_graph", etc.],
    "options": ["A) option1", "B) option2", ...],
    "variables": ["x", "y", "z", ...],
    "visual_elements": ["diagram", "graph", "geometric_figure", "none"]
}

CRITICAL MCQ DETECTION RULES:
- If you see numbered options like "(1)", "(2)", "(3)", "(4)" OR lettered options like "A)", "B)", "C)", "D)" in EITHER the OCR text OR the image, then this is DEFINITELY type "mcq"
- If the problem asks "What percentage", "Which of the following", "Select the correct", or similar choice questions, it's type "mcq"
- For MCQ problems, convert numbered options (1), (2), (3), (4) to lettered format A), B), C), D) in the options array
- Examples: "(1) 35%" becomes "A) 35%", "(2) 20%" becomes "B) 20%", etc.

Guidelines:
- Use the image to correct any OCR errors in the text
- If you see mathematical symbols, diagrams, or figures in the image that aren't captured in the OCR text, include them in your analysis
- For geometric problems, describe the shapes, measurements, and spatial relationships you see
- For graphs, describe axes, curves, and key points visible in the image
- For MCQ problems, ensure ALL options are captured and formatted correctly as A), B), C), D)
- Be specific about what the problem is asking for based on both text and visual cues
- Include mathematical expressions in LaTeX format when possible

SPECIAL INSTRUCTIONS FOR COUNTING/COMPARISON PROBLEMS:
If the problem involves counting objects, calculating ratios, finding totals, or comparing quantities:
- Identify ALL distinct objects/shapes in the image (circles, triangles, rectangles, etc.)
- Count each type of object systematically, going through the image methodically
- For visual counting problems, describe where each object is located in the image
- Break down complex calculations into step-by-step human reasoning
- For ratio problems, clearly identify what needs to be compared to what
- Example approach: "Count circles: [list each one], Count triangles: [list each one], Total shapes = circles + triangles + rectangles, Ratio = circles : (triangles + rectangles)"

CRITICAL: Return ONLY the JSON object, no explanation, no markdown formatting, no additional text.
"""
        return prompt

    def _create_vision_parsing_prompt(self, ocr_text: str, latex: Optional[str] = None) -> str:
        """Create a detailed prompt for vision-based problem parsing"""
        prompt = f"""
Analyze both the extracted text and the original image to parse this mathematics problem into a structured JSON format.

Extracted Text from OCR: {ocr_text}
"""
        
        if latex:
            prompt += f"LaTeX from OCR: {latex}\n"
        
        prompt += """
Please examine the image carefully for:
- Mathematical symbols that OCR might have missed
- Diagrams, graphs, or geometric figures
- Complex mathematical notation
- Any visual context that would help understand the problem

IMPORTANT: Return ONLY a valid JSON object with this exact structure:
{
    "type": "equation|system|integral|derivative|word_problem|mcq|geometry|graph_analysis|other",
    "statement": "The complete problem statement incorporating both text and visual elements",
    "asks": ["solve_for:x", "simplify", "compute_value", "find_derivative", "analyze_graph", etc.],
    "options": ["A) option1", "B) option2", ...],
    "variables": ["x", "y", "z", ...],
    "visual_elements": ["diagram", "graph", "geometric_figure", "none"]
}

CRITICAL MCQ DETECTION RULES:
- If the text contains numbered options like "(1)", "(2)", "(3)", "(4)" OR lettered options like "A)", "B)", "C)", "D)", then this is DEFINITELY type "mcq"
- If the text asks "What percentage", "Which of the following", "Select the correct", or similar choice questions, it's type "mcq"
- For MCQ problems, convert numbered options (1), (2), (3), (4) to lettered format A), B), C), D) in the options array
- Examples: "(1) 35%" becomes "A) 35%", "(2) 20%" becomes "B) 20%", etc.

Guidelines:
- Use the image to correct or enhance the OCR text
- Include mathematical expressions in LaTeX format when possible
- Identify the problem type based on both text and visual elements - ESPECIALLY detect MCQ correctly!
- For geometric problems, describe the shapes and measurements visible
- For graphs, describe axes, curves, and key points
- For MCQ problems, list ALL options in standardized A), B), C), D) format
- Be specific about what the problem is asking for

CRITICAL: Return ONLY the JSON object, no explanation, no markdown formatting, no additional text.
"""
        return prompt
    
    def _create_parsing_prompt(self, ocr_text: str, latex: Optional[str] = None) -> str:
        """Create a detailed prompt for problem parsing"""
        prompt = f"""
Parse the following mathematics problem into a structured JSON format.

OCR Text: {ocr_text}
"""
        
        if latex:
            prompt += f"LaTeX: {latex}\n"
        
        prompt += """
Return a JSON object with the following structure:
{
    "type": "equation|system|integral|derivative|word_problem|mcq|other",
    "statement": "The complete problem statement in LaTeX and/or plain text",
    "asks": ["solve_for:x", "simplify", "compute_value", "find_derivative", etc.],
    "options": ["A) option1", "B) option2", ...] (for MCQ only),
    "variables": ["x", "y", "z", ...] (list of variables in the problem),
    "confidence": 0.0-1.0 (how confident you are in this parsing based on text clarity)
}

IMPORTANT MCQ DETECTION RULES:
- If the text contains numbered options like "(1)", "(2)", "(3)", "(4)" OR lettered options like "A)", "B)", "C)", "D)", then this is definitely type "mcq"
- If the text asks "What percentage", "Which of the following", "Select the correct", or similar choice questions, it's type "mcq"
- For MCQ problems, convert numbered options (1), (2), (3), (4) to lettered format A), B), C), D) in the options array

Guidelines:
- "type": Choose the most appropriate type. Be especially careful to detect MCQ problems correctly!
- "statement": Include the complete problem statement, prefer LaTeX for mathematical expressions
- "asks": List what the problem is asking for (e.g., "solve_for:x", "simplify", "find_integral", "compute_value")
- "options": For MCQ problems, list ALL the options in A), B), C), D) format
- "variables": List all variables present in the problem
- "confidence": Rate 0.0-1.0 based on how clear and complete the OCR text appears
  - 1.0: Perfect, clear mathematical text
  - 0.8: Good text with minor issues
  - 0.6: Some unclear parts but generally readable
  - 0.4: Significant OCR errors or missing content
  - 0.2: Very poor OCR quality
  - 0.0: Completely unreadable or no mathematical content

Examples:
- Equation: "Solve x^2 + 2x + 1 = 0" → type: "equation", asks: ["solve_for:x"], confidence: 0.9
- MCQ: "What is 2+2? (1) 3 (2) 4 (3) 5" → type: "mcq", options: ["A) 3", "B) 4", "C) 5"], asks: ["compute_value"]
- Word problem: "A car travels..." → type: "word_problem", asks: ["find_distance", "find_time"]

Return only the JSON object, no additional text.
"""
        return prompt


# Global instance
parser_service = ParserService()
