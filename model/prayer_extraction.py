import re
import json
from typing import List, Dict, Optional

def extract_prayers_from_text(text: str) -> List[Dict]:
    """
    Extract prayers from the Treasure House of Prayers document.
    
    Args:
        text: The raw text content from the PDF
        
    Returns:
        List of dictionaries containing prayer information
    """
    prayers = []
    prayer_id = 1
    
    # Split text into sections by page numbers or prayer headers
    # Look for patterns like "Prayer for..." or "Du'a..." or prayer titles
    
    # Pattern to match prayer sections
    # Looks for: Title, Hadrat/Background, Reference number, Arabic text, Translation
    
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line is a prayer title (starts with "Prayer" or contains prayer keywords)
        if is_prayer_title(line):
            prayer = {
                "id": prayer_id,
                "title": clean_title(line),
                "background": "",
                "reference": "",
                "meaning": "",
                "arabic": []
            }
            
            i += 1
            
            # Extract background (Hadrat... relates...)
            background_lines = []
            while i < len(lines) and not is_arabic_text(lines[i]) and not is_reference(lines[i]):
                if lines[i].strip() and not is_prayer_title(lines[i]):
                    background_lines.append(lines[i].strip())
                i += 1
            
            prayer["background"] = ' '.join(background_lines)
            
            # Extract Arabic text
            arabic_lines = []
            while i < len(lines) and is_arabic_text(lines[i]):
                arabic_lines.append(lines[i].strip())
                i += 1
            
            prayer["arabic"] = arabic_lines
            
            # Extract reference number (usually a standalone number)
            if i < len(lines) and is_reference(lines[i]):
                prayer["reference"] = lines[i].strip()
                i += 1
            
            # Extract meaning/translation
            meaning_lines = []
            while i < len(lines) and not is_prayer_title(lines[i]) and not is_arabic_text(lines[i]):
                if lines[i].strip() and not is_reference(lines[i]):
                    meaning_lines.append(lines[i].strip())
                    if is_end_of_prayer(lines[i]):
                        break
                i += 1
            
            prayer["meaning"] = ' '.join(meaning_lines)
            
            # Only add if we have meaningful content
            if prayer["title"] and (prayer["arabic"] or prayer["meaning"]):
                prayers.append(prayer)
                prayer_id += 1
        else:
            i += 1
    
    return prayers


def is_prayer_title(line: str) -> bool:
    """Check if a line is a prayer title."""
    title_keywords = [
        'Prayer for', 'Prayer of', 'Prayer on', 'Prayer at',
        'Du\'a', 'Dua', 'Prayers for', 'Prayers of',
        'Durud', 'Istikharah', 'Salatut-Tasbih'
    ]
    line = line.strip()
    return any(keyword in line for keyword in title_keywords) and len(line) < 150


def is_arabic_text(line: str) -> bool:
    """Check if a line contains Arabic text."""
    # Check for Arabic Unicode range
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(line))


def is_reference(line: str) -> bool:
    """Check if a line is a reference number."""
    line = line.strip()
    # Check if it's just a number or a short reference
    return line.isdigit() or (len(line) < 10 and re.match(r'^\d+', line)) # type: ignore


def is_end_of_prayer(line: str) -> bool:
    """Check if we've reached the end of a prayer section."""
    end_markers = ['Note:', 'Hadrat', 'Another', 'As per']
    return any(marker in line for marker in end_markers)


def clean_title(title: str) -> str:
    """Clean up the prayer title."""
    # Remove extra whitespace and page numbers
    title = re.sub(r'\s+', ' ', title)
    title = re.sub(r'\d{1,3}$', '', title)  # Remove trailing page numbers
    return title.strip()


def extract_from_document(file_path: str) -> List[Dict]:
    """
    Main function to extract prayers from a PDF or text file.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        List of extracted prayers
    """
    try:
        # For text files
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            # For PDF files, you'd need PyPDF2 or pdfplumber
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
        
        prayers = extract_prayers_from_text(text)
        return prayers
    
    except Exception as e:
        print(f"Error extracting prayers: {e}")
        return []


def save_prayers_to_json(prayers: List[Dict], output_file: str = 'prayers.json'):
    """
    Save extracted prayers to a JSON file.
    
    Args:
        prayers: List of prayer dictionaries
        output_file: Output JSON file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prayers, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(prayers)} prayers to {output_file}")


# Manual extraction helper for the provided text
def extract_prayers_manually(document_text: str) -> List[Dict]:
    """
    Manually structured extraction based on the document format.
    This provides better accuracy for the specific document structure.
    """
    prayers = []
    
    # Predefined prayers based on the document structure
    prayer_data = [
        {
            "id": 1,
            "title": "Prayer for Blessings in Intentions and Actions",
            "background": "Hadrat Abu-Bakr Siddiq (ra) relates that whenever the Holy Prophet (sa) intended to do something he used to pray:",
            "reference": "45",
            "arabic_pattern": r"اَللّٰهُمَّ خِرْىلِ وَاخْتَرْىلِ",
            "meaning": "O Allah, bestow means of goodness on me and choose best for me."
        },
        {
            "id": 2,
            "title": "Prayer for Attaining Love of God",
            "background": "'Abdullah bin Yazid Al-Ansari (ra) relates the Holy Prophet (sa) offered this prayer for attaining love of God along with his other prayers:",
            "reference": "46",
            "arabic_pattern": r"اَللّٰهُمَّ ارْزُقْىنِْ حُبَّکَ",
            "meaning": "O Allah, bestow on me Your love and the love of that which would benefit me before You."
        },
        # Add more prayers as needed...
    ]
    
    # Search for each prayer in the document
    for prayer_template in prayer_data:
        # Find Arabic text using pattern
        arabic_match = re.search(prayer_template["arabic_pattern"], document_text)
        if arabic_match:
            # Extract full Arabic text (usually until ۔)
            start_pos = arabic_match.start()
            end_marker = document_text.find('۔', start_pos)
            if end_marker != -1:
                arabic_text = document_text[start_pos:end_marker+1].strip()
                prayer_template["arabic"] = [arabic_text]
            
            prayers.append({
                "id": prayer_template["id"],
                "title": prayer_template["title"],
                "background": prayer_template["background"],
                "reference": prayer_template["reference"],
                "meaning": prayer_template["meaning"],
                "arabic": prayer_template.get("arabic", [])
            })
    
    return prayers


# Example usage
if __name__ == "__main__":
    # Example 1: Extract from file
    # prayers = extract_from_document('prayers.txt')
    
    # Example 2: Extract from provided text
    sample_text = """
    Your PDF text content here...
    """
    
    prayers = extract_prayers_from_text(sample_text)
    
    # Save to JSON
    save_prayers_to_json(prayers, 'prayers.json')
    
    # Print summary
    print(f"\nExtracted {len(prayers)} prayers")
    for prayer in prayers[:3]:  # Show first 3
        print(f"\n{prayer['id']}. {prayer['title']}")
        print(f"   Reference: {prayer['reference']}")