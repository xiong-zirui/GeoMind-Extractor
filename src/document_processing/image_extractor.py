"""
Image extraction module for PDF documents.
Extracts all images from PDFs and saves them with metadata.
"""
import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import json
from datetime import datetime

class ImageExtractor:
    """Extract images from PDF documents and save them with metadata."""
    
    def __init__(self, output_dir: str = "data/processed/images"):
        """
        Initialize the image extractor.
        
        Args:
            output_dir: Directory to save extracted images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_images_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract all images from a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing image metadata and file paths
        """
        logging.info(f"Starting image extraction from: {pdf_path.name}")
        
        # Create subdirectory for this PDF's images
        pdf_images_dir = self.output_dir / pdf_path.stem
        pdf_images_dir.mkdir(exist_ok=True)
        
        extracted_images = []
        
        try:
            doc = fitz.open(pdf_path)
            total_images = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                logging.info(f"Page {page_num + 1}: Found {len(image_list)} images")
                
                for img_index, img in enumerate(image_list):
                    # Get the XREF of the image
                    xref = img[0]
                    
                    try:
                        # Extract the image
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Create filename
                        image_filename = f"{pdf_path.stem}_page{page_num + 1:03d}_img{img_index + 1:03d}.{image_ext}"
                        image_path = pdf_images_dir / image_filename
                        
                        # Save the image
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # Get image dimensions and additional info
                        try:
                            with Image.open(io.BytesIO(image_bytes)) as pil_img:
                                width, height = pil_img.size
                                mode = pil_img.mode
                        except Exception as e:
                            logging.warning(f"Could not get PIL info for image {image_filename}: {e}")
                            width = height = mode = "unknown"
                        
                        # Create metadata
                        image_metadata = {
                            "filename": image_filename,
                            "filepath": str(image_path),
                            "source_pdf": pdf_path.name,
                            "page_number": page_num + 1,
                            "image_index_on_page": img_index + 1,
                            "xref": xref,
                            "format": image_ext,
                            "width": width,
                            "height": height,
                            "color_mode": mode,
                            "file_size_bytes": len(image_bytes),
                            "extraction_timestamp": datetime.now().isoformat(),
                            "bbox": img[1:5] if len(img) > 4 else None,  # Bounding box if available
                        }
                        
                        extracted_images.append(image_metadata)
                        total_images += 1
                        
                        logging.info(f"Extracted: {image_filename} ({width}x{height}, {len(image_bytes)} bytes)")
                        
                    except Exception as e:
                        logging.error(f"Failed to extract image {img_index + 1} from page {page_num + 1}: {e}")
                        continue
            
            doc.close()
            
            # Save metadata to JSON file
            metadata_file = pdf_images_dir / f"{pdf_path.stem}_images_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "source_pdf": str(pdf_path),
                    "extraction_timestamp": datetime.now().isoformat(),
                    "total_images_extracted": total_images,
                    "images": extracted_images
                }, f, indent=2, ensure_ascii=False)
            
            logging.info(f"✅ Successfully extracted {total_images} images from {pdf_path.name}")
            logging.info(f"📁 Images saved to: {pdf_images_dir}")
            logging.info(f"📋 Metadata saved to: {metadata_file}")
            
            return extracted_images
            
        except Exception as e:
            logging.error(f"Failed to extract images from {pdf_path}: {e}")
            return []
    
    def get_image_statistics(self, extracted_images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about extracted images.
        
        Args:
            extracted_images: List of image metadata dictionaries
            
        Returns:
            Dictionary containing image statistics
        """
        if not extracted_images:
            return {"total_images": 0}
        
        formats = {}
        total_size = 0
        sizes = []
        pages_with_images = set()
        
        for img in extracted_images:
            # Count formats
            fmt = img.get("format", "unknown")
            formats[fmt] = formats.get(fmt, 0) + 1
            
            # Sum file sizes
            size = img.get("file_size_bytes", 0)
            total_size += size
            
            # Collect dimensions
            width = img.get("width", 0)
            height = img.get("height", 0)
            if isinstance(width, int) and isinstance(height, int):
                sizes.append((width, height))
            
            # Track pages with images
            pages_with_images.add(img.get("page_number"))
        
        # Calculate average dimensions
        if sizes:
            avg_width = sum(w for w, h in sizes) / len(sizes)
            avg_height = sum(h for w, h in sizes) / len(sizes)
            max_width = max(w for w, h in sizes)
            max_height = max(h for w, h in sizes)
            min_width = min(w for w, h in sizes)
            min_height = min(h for w, h in sizes)
        else:
            avg_width = avg_height = max_width = max_height = min_width = min_height = 0
        
        return {
            "total_images": len(extracted_images),
            "formats": formats,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "pages_with_images": len(pages_with_images),
            "page_numbers_with_images": sorted(pages_with_images),
            "dimensions": {
                "average_width": round(avg_width, 1),
                "average_height": round(avg_height, 1),
                "max_width": max_width,
                "max_height": max_height,
                "min_width": min_width,
                "min_height": min_height
            }
        }
    
    def extract_and_analyze(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract images and return complete analysis.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted images and statistics
        """
        extracted_images = self.extract_images_from_pdf(pdf_path)
        statistics = self.get_image_statistics(extracted_images)
        
        return {
            "extraction_summary": {
                "source_pdf": str(pdf_path),
                "timestamp": datetime.now().isoformat(),
                **statistics
            },
            "images": extracted_images
        }

def extract_images_from_pdf(pdf_path: Path, output_dir: str = "data/processed/images") -> Dict[str, Any]:
    """
    Convenience function to extract images from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images
        
    Returns:
        Dictionary containing extraction results and statistics
    """
    extractor = ImageExtractor(output_dir)
    return extractor.extract_and_analyze(pdf_path)

if __name__ == "__main__":
    # Test the image extractor
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        if pdf_file.exists():
            result = extract_images_from_pdf(pdf_file)
            print(f"✅ Extracted {result['extraction_summary']['total_images']} images")
        else:
            print(f"❌ File not found: {pdf_file}")
    else:
        print("Usage: python image_extractor.py <pdf_file>")
