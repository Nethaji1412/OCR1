"""
PDF Layout Preserving Formatter
Maintains original PDF formatting, fonts, and alignment after translation
"""

import fitz
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

@dataclass
class FormattedText:
    """Text with preserved formatting"""
    text: str
    x: float
    y: float
    font_name: str
    font_size: float
    is_bold: bool
    is_italic: bool
    alignment: str  # left, center, right, justify
    color: Tuple[float, float, float] = (0, 0, 0)


class PDFLayoutPreserver:
    """
    Preserves PDF layout, fonts, and formatting during text extraction and reconstruction
    """
    
    def __init__(self):
        """Initialize PDF layout preserver"""
        print("Initializing PDF Layout Preserver...")
        self.formatted_text_blocks = []
    
    def extract_with_formatting(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF while preserving formatting information
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dict with text and formatting metadata
        """
        try:
            doc = fitz.open(pdf_path)
            all_blocks = []
            pages_data = []
            
            for page_num, page in enumerate(doc):
                page_dict = page.get_text("dict")
                blocks = page_dict["blocks"]
                
                page_blocks = []
                page_text = ""
                
                for block in blocks:
                    if "lines" in block:  # Text block
                        for line_idx, line in enumerate(block["lines"]):
                            for span_idx, span in enumerate(line["spans"]):
                                text = span["text"].strip()
                                
                                if text:
                                    # Extract all formatting
                                    bbox = span["bbox"]
                                    font_size = span["size"]
                                    font_name = span["font"]
                                    flags = span.get("flags", 0)
                                    color = span.get("color", 0)
                                    
                                    # Extract color
                                    if isinstance(color, int):
                                        r = (color >> 16) & 255
                                        g = (color >> 8) & 255
                                        b = color & 255
                                        color_tuple = (r/255, g/255, b/255)
                                    else:
                                        color_tuple = (0, 0, 0)
                                    
                                    # Check formatting flags
                                    is_bold = bool(flags & 0b0001)
                                    is_italic = bool(flags & 0b0010)
                                    
                                    # Determine alignment
                                    x_center = (bbox[0] + bbox[2]) / 2
                                    page_width = page.rect.width
                                    
                                    if abs(x_center - page_width / 2) < page_width * 0.1:
                                        alignment = "center"
                                    elif x_center < page_width * 0.3:
                                        alignment = "left"
                                    else:
                                        alignment = "right"
                                    
                                    formatted_block = FormattedText(
                                        text=text,
                                        x=bbox[0],
                                        y=bbox[1],
                                        font_name=font_name,
                                        font_size=font_size,
                                        is_bold=is_bold,
                                        is_italic=is_italic,
                                        alignment=alignment,
                                        color=color_tuple
                                    )
                                    
                                    page_blocks.append(formatted_block)
                                    page_text += text + " "
                                    all_blocks.append(formatted_block)
                
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': page_text.strip(),
                    'blocks': page_blocks,
                    'width': page.rect.width,
                    'height': page.rect.height
                })
            
            doc.close()
            
            return {
                'status': 'success',
                'pages': pages_data,
                'blocks': all_blocks,
                'page_count': len(pages_data),
                'block_count': len(all_blocks)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'pages': [],
                'blocks': []
            }
    
    def create_formatted_pdf(self, translated_blocks: List[FormattedText], 
                            output_path: str, page_data: List[Dict]) -> bool:
        """
        Create new PDF with translated text maintaining original formatting
        
        Args:
            translated_blocks: List of FormattedText with translated content
            output_path: Where to save the output PDF
            page_data: Original page data for layout reference
        
        Returns:
            Success status
        """
        try:
            # Create PDF canvas
            pdf_buffer = io.BytesIO()
            
            # Determine page size
            page_width = page_data[0]['width'] / 72 * inch if page_data else 8.5 * inch
            page_height = page_data[0]['height'] / 72 * inch if page_data else 11 * inch
            
            c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
            
            current_page = 0
            
            for block in translated_blocks:
                # Convert position (PDFs use bottom-left origin)
                x = block.x / 72 * inch
                y = (page_data[current_page]['height'] - block.y) / 72 * inch
                
                # Select font
                font_name = "Helvetica"  # Fallback
                if block.is_bold and block.is_italic:
                    font_name = "Helvetica-BoldOblique"
                elif block.is_bold:
                    font_name = "Helvetica-Bold"
                elif block.is_italic:
                    font_name = "Helvetica-Oblique"
                
                # Set text color
                c.setFillColorRGB(*block.color)
                
                # Set font
                c.setFont(font_name, block.font_size)
                
                # Draw text with alignment
                if block.alignment == "center":
                    c.drawCentredString(x, y, block.text)
                elif block.alignment == "right":
                    c.drawRightString(x, y, block.text)
                else:  # left
                    c.drawString(x, y, block.text)
            
            c.save()
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            return True
        
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return False
    
    def get_text_by_page(self, pages_data: List[Dict]) -> List[str]:
        """Extract text organized by page"""
        return [page['text'] for page in pages_data]
    
    def update_translated_text(self, blocks: List[FormattedText], 
                               translations: Dict[str, str]) -> List[FormattedText]:
        """
        Update blocks with translated text while preserving formatting
        
        Args:
            blocks: Original blocks with formatting
            translations: Dict mapping original text to translated text
        
        Returns:
            Updated blocks with translated text
        """
        updated_blocks = []
        
        for block in blocks:
            # Create copy of block
            new_block = FormattedText(
                text=translations.get(block.text, block.text),  # Use translation or original
                x=block.x,
                y=block.y,
                font_name=block.font_name,
                font_size=block.font_size,
                is_bold=block.is_bold,
                is_italic=block.is_italic,
                alignment=block.alignment,
                color=block.color
            )
            updated_blocks.append(new_block)
        
        return updated_blocks


# Example usage
if __name__ == "__main__":
    preserver = PDFLayoutPreserver()
    
    # Extract with formatting
    result = preserver.extract_with_formatting("sample.pdf")
    
    if result['status'] == 'success':
        print(f"Extracted {result['page_count']} pages")
        print(f"Found {result['block_count']} text blocks")
        
        # Get text by page
        texts = preserver.get_text_by_page(result['pages'])
        print("Page texts:", texts)
