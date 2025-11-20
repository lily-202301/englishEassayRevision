"""
PDF generation service using Jinja2 and WeasyPrint.
"""
import re
import logging
from typing import List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from app.schemas import FullReport, SentenceAnalysis

# Configure logging
logger = logging.getLogger(__name__)

# Setup Jinja2 environment
template_dir = Path(__file__).parent.parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)


def create_annotated_html(original_text: str, analysis_list: List[SentenceAnalysis]) -> str:
    """
    Create HTML with error annotations by wrapping error parts in <span class='error'> tags.
    Uses re.sub to safely replace only the first occurrence of error phrases within sentences.
    
    Args:
        original_text: The original English text
        analysis_list: List of sentence analysis results
    
    Returns:
        str: HTML string with error annotations
    """
    if not analysis_list:
        # If no analysis, return original text wrapped in paragraph
        return f"<p>{original_text}</p>"
    
    annotated_text = original_text
    processed_sentences = set()  # Track which sentences we've already processed
    
    # Process each analysis item
    for analysis in analysis_list:
        original_sentence = analysis.original.strip()
        error_text = analysis.error
        
        # Skip if no error or sentence already processed
        if not error_text or not original_sentence or original_sentence in processed_sentences:
            continue
        
        # Find the first occurrence of the original sentence in the text
        sentence_match = re.search(re.escape(original_sentence), annotated_text)
        if not sentence_match:
            continue
        
        # Extract the sentence from the text
        sentence_start = sentence_match.start()
        sentence_end = sentence_match.end()
        sentence_in_text = annotated_text[sentence_start:sentence_end]
        
        # Try to find error text within this specific sentence occurrence
        error_match = re.search(re.escape(error_text), sentence_in_text, re.IGNORECASE)
        
        if error_match:
            # Error found within the sentence - replace only this occurrence
            error_start_in_sentence = error_match.start()
            error_end_in_sentence = error_match.end()
            
            # Create annotated sentence
            annotated_sentence = (
                sentence_in_text[:error_start_in_sentence] +
                f"<span class='error'>{error_text}</span>" +
                sentence_in_text[error_end_in_sentence:]
            )
            
            # Replace the sentence at the specific position we found
            annotated_text = (
                annotated_text[:sentence_start] +
                annotated_sentence +
                annotated_text[sentence_end:]
            )
            
            processed_sentences.add(original_sentence)
        else:
            # Error not found in sentence - mark as processed to avoid retrying
            processed_sentences.add(original_sentence)
            logger.debug(
                f"Error text '{error_text}' not found in sentence '{original_sentence[:50]}...'"
            )
    
    # Wrap in paragraph tags if not already wrapped
    if not annotated_text.startswith('<'):
        annotated_text = f"<p>{annotated_text}</p>"
    
    return annotated_text


def generate_pdf(report_data: FullReport, original_text: str) -> bytes:
    """
    Generate PDF from report data using Jinja2 template and WeasyPrint.
    
    Args:
        report_data: FullReport object containing analysis results
        original_text: The original English text (for error annotation)
    
    Returns:
        bytes: PDF file content as bytes
    
    Raises:
        FileNotFoundError: If template file is not found
        Exception: If PDF generation fails
    """
    try:
        logger.info("Starting PDF generation")
        
        # Load template
        template = env.get_template("report.html")
        
        # Prepare template context
        context = {
            "writing_goal_analysis": report_data.writing_goal_analysis,
            "sentence_analysis": report_data.sentence_analysis,
            "polished_version": report_data.polished_version,
            "annotated_html": create_annotated_html(
                original_text,
                report_data.sentence_analysis
            )
        }
        
        # Render template
        html_content = template.render(**context)
        logger.info("Template rendered successfully")
        
        # Generate PDF using WeasyPrint
        pdf_bytes = HTML(string=html_content).write_pdf()
        logger.info("PDF generated successfully")
        
        return pdf_bytes
    
    except FileNotFoundError as e:
        error_msg = f"Template file not found: {e}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to generate PDF: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

