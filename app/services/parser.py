import openai
import json
import logging
import base64
from typing import Optional
from config.settings import settings
from app.models import ParsedProblem, ProblemType

logger = logging.getLogger(__name__)


class ParserService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.confidence_threshold = 0.7  # Threshold for using image fallback
    
    async def parse_problem(self, ocr_text: str, latex: Optional[str] = None, image_content: Optional[bytes] = None) -> ParsedProblem:
        """
        Parse OCR output into structured problem format using LLM
        If OCR confidence is low and image is provided, use vision model for better context
        """
        try:
            # First attempt: Parse with text only
            logger.info("🤖 Attempting OpenAI parsing with text only...")
            prompt = self._create_parsing_prompt(ocr_text, latex)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a mathematics problem parser. Parse the given text into a structured JSON format. Include a 'confidence' field (0.0-1.0) indicating how confident you are in the parsing."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            # Check confidence level and visual indicators
            parsing_confidence = parsed_data.get('confidence', 1.0)
            logger.info(f"🤖 OpenAI parsing confidence: {parsing_confidence}")
            
            # Check for visual indicators that suggest image content is needed
            visual_indicators = [
                "figure below", "diagram", "graph", "picture", "image", 
                "shown below", "illustrated", "geometric", "triangle", "rectangle",
                "circle", "coordinate", "plot", "chart", "table", "grid"
            ]
            
            text_lower = ocr_text.lower()
            has_visual_indicators = any(indicator in text_lower for indicator in visual_indicators)
            
            # Trigger image fallback if:
            # 1. Low parsing confidence OR
            # 2. Text mentions visual elements but we only have text
            should_use_image = (parsing_confidence < self.confidence_threshold) or (has_visual_indicators and image_content)
            
            if should_use_image and image_content:
                if parsing_confidence < self.confidence_threshold:
                    logger.info(f"⚠️ Low confidence ({parsing_confidence} < {self.confidence_threshold}), retrying with image...")
                else:
                    logger.info(f"🔍 Visual elements detected in text ({[i for i in visual_indicators if i in text_lower]}), using image for better context...")
                
                return await self._parse_with_image(ocr_text, image_content, latex)
            
            # Remove confidence from final result (not part of ParsedProblem model)
            parsed_data.pop('confidence', None)
            return ParsedProblem(**parsed_data)
            
        except Exception as e:
            logger.error(f"Problem parsing failed: {e}")
            
            # If text parsing failed and we have image, try with vision model
            if image_content:
                logger.info("🔄 Text parsing failed, attempting with image...")
                try:
                    return await self._parse_with_image(ocr_text, image_content, latex)
                except Exception as vision_error:
                    logger.error(f"Vision parsing also failed: {vision_error}")
            
            # Return a basic fallback structure
            return ParsedProblem(
                type=ProblemType.OTHER,
                statement=ocr_text,
                asks=["solve"],
                options=[],
                variables=[]
            )
    
    async def _parse_with_image(self, ocr_text: str, image_content: bytes, latex: Optional[str] = None) -> ParsedProblem:
        """
        Parse problem using OpenAI vision model with both text and image context
        """
        try:
            logger.info("🔍 Using OpenAI vision model for enhanced parsing...")
            
            # Convert image to base64
            image_b64 = base64.b64encode(image_content).decode()
            
            # Create vision prompt
            vision_prompt = self._create_vision_parsing_prompt(ocr_text, latex)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use the latest vision model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a mathematics problem parser with vision capabilities. Analyze both the extracted text and the original image to parse the problem into a structured JSON format."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": vision_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            logger.info("✅ OpenAI vision parsing successful!")
            
            # Parse the response
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
            logger.error(f"Vision parsing failed: {e}")
            raise
    
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

Guidelines:
- Use the image to correct or enhance the OCR text
- Include mathematical expressions in LaTeX format when possible
- Identify the problem type based on both text and visual elements
- For geometric problems, describe the shapes and measurements visible
- For graphs, describe axes, curves, and key points
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

Guidelines:
- "type": Choose the most appropriate type based on the problem
- "statement": Include the complete problem statement, prefer LaTeX for mathematical expressions
- "asks": List what the problem is asking for (e.g., "solve_for:x", "simplify", "find_integral")
- "options": Only include if this is a multiple choice question
- "variables": List all variables present in the problem
- "confidence": Rate 0.0-1.0 based on how clear and complete the OCR text appears
  - 1.0: Perfect, clear mathematical text
  - 0.8: Good text with minor issues
  - 0.6: Some unclear parts but generally readable
  - 0.4: Significant OCR errors or missing content
  - 0.2: Very poor OCR quality
  - 0.0: Completely unreadable or no mathematical content

Examples:
- Equation: "Solve x^2 + 2x + 1 = 0" → asks: ["solve_for:x"], confidence: 0.9
- Integral: "Find ∫x²dx" → asks: ["find_integral"], confidence: 0.8
- Word problem: "A car travels..." → asks: ["find_distance", "find_time"], confidence: 0.7

Return only the JSON object, no additional text.
"""
        return prompt


# Global instance
parser_service = ParserService()
