"""
TTS Text Formatter
Comprehensive text formatting for Text-to-Speech processing of Reddit posts
"""

import re
import unicodedata

# AITA/Reddit Abbreviations Dictionary
ABBREVIATIONS_DICT = {
    # Primary AITA/Judgment Abbreviations
    "AITA": "Am I The Asshole",
    "AITAH": "Am I The Asshole Here", 
    "WIBTA": "Would I Be The Asshole",
    "WIBTAH": "Would I Be The Asshole Here",
    "NTA": "Not The Asshole",
    "YTA": "You're The Asshole", 
    "ESH": "Everyone Sucks Here",
    "NAH": "No Assholes Here",
    "INFO": "Need More Information",
    
    # Family Relationships
    "SO": "Significant Other",
    "BF": "Boyfriend",
    "GF": "Girlfriend", 
    "EX": "Ex",
    "DH": "Dear Husband",
    "DW": "Dear Wife",
    "MIL": "Mother-In-Law",
    "FIL": "Father-In-Law",
    "SIL": "Sister-In-Law",
    "BIL": "Brother-In-Law",
    "DIL": "Daughter-In-Law",
    "LDR": "Long Distance Relationship",
    "BD": "Baby Daddy",
    "BM": "Baby Mama",
    
    # Common Phrases and Situations
    "WTF": "What The F word",
    "TBH": "To Be Honest",
    "FWIW": "For What It's Worth",
    "IMHO": "In My Humble Opinion",
    "IMO": "In My Opinion",
    "FYI": "For Your Information",
    "BTW": "By The Way",
    "AFAIK": "As Far As I Know",
    "IIRC": "If I Recall Correctly",
    "ETA": "Edited To Add",
    "TLDR": "Too Long Didn't Read",
    "TL;DR": "Too Long Didn't Read",
    
    # Emotions and Reactions
    "SMH": "Shaking My Head",
    "FML": "F My Life",
    "JFC": "Jesus F-ing Christ",
    "OMG": "Oh My God",
    "WTH": "What The Hell",
    "IDK": "I Don't Know",
    "IDC": "I Don't Care",
    "IDGAF": "I Don't Give A F word",
    
    # Relationship/Social Situations
    "NC": "No Contact",
    "LC": "Low Contact",
    "VLC": "Very Low Contact",
    "JNMIL": "Just No Mother-In-Law",
    "JNFIL": "Just No Father-In-Law",
    "STBX": "Soon To Be Ex",
    "AP": "Affair Partner",
    "OW": "Other Woman",
    "OM": "Other Man",
    
    # Additional Common Ones
    "SAHM": "Stay At Home Mom",
    "SAHD": "Stay At Home Dad",
    "LO": "Little One",
    "DD": "Dear Daughter",
    "DS": "Dear Son",
    "DSD": "Dear Step Daughter",
    "DSS": "Dear Step Son",
    "SM": "Step Mother",
    "SF": "Step Father",
    "JK": "Just Kidding",
    "NVM": "Never Mind",
    "FFS": "For F's Sake",
    "GTFO": "Get The F Out",
    "DGAF": "Don't Give A F word"
}

def fix_encoding_issues(text):
    """Fix common encoding issues found in the data."""
    # Dictionary of common encoding problems
    encoding_fixes = {
        'â€™': "'",  # Smart apostrophe
        'â€œ': '"',  # Smart quote open
        'â€\x9d': '"',  # Smart quote close
        'â€"': '—',  # Em dash
        'â€"': '–',  # En dash
        'â€¦': '...',  # Ellipsis
        'â€¢': '•',  # Bullet point
        'Â': ' ',   # Non-breaking space issues
        'â€\x9c': '"',  # Another smart quote variant
        'â€™s': "'s", # Possessive
        'â€™t': "'t", # Contractions like don't, won't
        'â€™m': "'m", # Contractions like I'm
        'â€™ve': "'ve", # Contractions like I've
        'â€™ll': "'ll", # Contractions like I'll
        'â€™re': "'re", # Contractions like you're
        'â€™d': "'d",  # Contractions like I'd
    }
    
    for bad, good in encoding_fixes.items():
        text = text.replace(bad, good)
    
    # Additional cleanup for any remaining weird characters
    text = unicodedata.normalize('NFKD', text)
    
    return text

def expand_abbreviations(text):
    """Expand abbreviations using the dictionary."""
    words = text.split()
    expanded_words = []
    
    for word in words:
        # Remove punctuation for matching but keep it for output
        clean_word = re.sub(r'[^\w]', '', word).upper()
        if clean_word in ABBREVIATIONS_DICT:
            # Find the punctuation
            punctuation = ''.join(c for c in word if not c.isalnum())
            expanded_words.append(ABBREVIATIONS_DICT[clean_word] + punctuation)
        else:
            expanded_words.append(word)
    
    return ' '.join(expanded_words)

def handle_age_gender_markers(text):
    """Convert age/gender markers like (19F) to readable format."""
    # Pattern for age/gender markers like (19F), (20M), etc.
    pattern = r'\((\d+)([MFmfNBnb]+)\)'
    
    def replace_marker(match):
        age = match.group(1)
        gender = match.group(2).upper()
        gender_map = {
            'M': 'year old male',
            'F': 'year old female', 
            'NB': 'year old non-binary'
        }
        gender_text = gender_map.get(gender, 'year old person')
        return f"{age} {gender_text}"
    
    return re.sub(pattern, replace_marker, text)

def handle_superscript_ordinals(text):
    """Convert superscript ordinals like 5^(th) to readable format."""
    # Handle superscript ordinals
    ordinal_pattern = r'(\d+)\^\(?(st|nd|rd|th)\)?'
    
    def replace_ordinal(match):
        number = int(match.group(1))
        if number == 1:
            return "first"
        elif number == 2:
            return "second"
        elif number == 3:
            return "third"
        elif number == 5:
            return "fifth"
        elif number == 8:
            return "eighth"
        elif number == 9:
            return "ninth"
        elif number == 12:
            return "twelfth"
        else:
            return f"{number}{match.group(2)}"
    
    return re.sub(ordinal_pattern, replace_ordinal, text)

def handle_currency_and_numbers(text):
    """Format currency and numbers for TTS."""
    # British pounds
    text = re.sub(r'£(\d+)', r'\1 pounds', text)
    text = re.sub(r'£(\d+)-£(\d+)', r'\1 to \2 pounds', text)
    
    # US dollars
    text = re.sub(r'\$(\d+)', r'\1 dollars', text)
    text = re.sub(r'\$(\d+)-\$(\d+)', r'\1 to \2 dollars', text)
    
    # Percentages
    text = re.sub(r'(\d+)%', r'\1 percent', text)
    
    # Time formats
    text = re.sub(r'(\d{1,2})am', r'\1 A.M.', text)
    text = re.sub(r'(\d{1,2})pm', r'\1 P.M.', text)
    text = re.sub(r'(\d{1,2}):(\d{2})\s*am', r'\1:\2 A.M.', text)
    text = re.sub(r'(\d{1,2}):(\d{2})\s*pm', r'\1:\2 P.M.', text)
    text = re.sub(r'(\d{1,2}):(\d{2})\s*p\.m\.', r'\1:\2 P.M.', text)
    
    return text

def handle_profanity_censoring(text):
    """Handle censored profanity for TTS."""
    profanity_replacements = {
        r'\bf\*\*\*\b': 'f word',
        r'\bf\*\*\*ing\b': 'f-ing',
        r'\bf\*\*\*ed\b': 'f-ed',
        r'\bs\*\*\*\b': 's word',
        r'\ba\*\*hole\b': 'a-hole',
        r'\ba\*\*\b': 'a word',
        # Context-aware AH replacement
        r'\bAH\b': 'asshole'  # In AITA context, AH usually means asshole
    }
    
    for pattern, replacement in profanity_replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def normalize_punctuation(text):
    """Normalize punctuation for better TTS flow."""
    # Multiple exclamation marks
    text = re.sub(r'!{2,}', '!', text)
    
    # Multiple question marks
    text = re.sub(r'\?{2,}', '?', text)
    
    # Multiple periods (but preserve intentional ellipsis)
    text = re.sub(r'\.{4,}', '...', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])\s*([a-zA-Z])', r'\1 \2', text)
    
    # Add periods to end sentences that don't have punctuation
    sentences = text.split('.')
    fixed_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and not sentence[-1] in '!?':
            if len(sentence.split()) > 3:  # Only for substantial sentences
                sentence += '.'
        fixed_sentences.append(sentence)
    
    text = ' '.join(fixed_sentences).strip()
    
    return text

def add_reading_pauses(text):
    """Add appropriate pauses for better TTS flow."""
    # Add pause after common transition words
    transitions = [
        'However', 'Meanwhile', 'Additionally', 'Furthermore', 'Nevertheless',
        'On the other hand', 'For example', 'In fact', 'As a result'
    ]
    
    for transition in transitions:
        text = re.sub(f'({transition})', f'{transition},', text, flags=re.IGNORECASE)
    
    # Add pauses before "So" when it starts explanation
    text = re.sub(r'\bSo\b(?=\s+[A-Z])', 'So,', text)
    
    return text

def improve_sentence_structure(text):
    """Improve sentence structure for TTS readability."""
    # Break up very long sentences (over 200 characters)
    sentences = re.split(r'([.!?])', text)
    improved_sentences = []
    
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i]
            punctuation = sentences[i+1] if i+1 < len(sentences) else ''
            
            if len(sentence) > 200:
                # Try to break at natural pause points
                break_points = [', but ', ', and ', ', so ', ', because ', ', when ', ', which ']
                for break_point in break_points:
                    if break_point in sentence:
                        parts = sentence.split(break_point, 1)
                        if len(parts) == 2 and len(parts[0]) > 50:
                            sentence = parts[0] + '.' + break_point.strip() + ' ' + parts[1].capitalize()
                            break
            
            improved_sentences.append(sentence + punctuation)
    
    return ''.join(improved_sentences)

def clean_whitespace(text):
    """Clean up excessive whitespace."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove spaces at beginning/end of lines
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    # Remove excessive newlines but preserve paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def format_text_for_tts(text, include_context_words=True):
    """
    Main function to format text for TTS processing.
    
    Args:
        text (str): Input text to format
        include_context_words (bool): Whether to add context words like "quote" for readability
    
    Returns:
        str: Formatted text ready for TTS
    """
    if not isinstance(text, str):
        return ""
    
    # Step 1: Fix encoding issues (CRITICAL)
    text = fix_encoding_issues(text)
    
    # Step 2: Handle age/gender markers
    text = handle_age_gender_markers(text)
    
    # Step 3: Handle superscript and special formatting
    text = handle_superscript_ordinals(text)
    
    # Step 4: Expand abbreviations
    text = expand_abbreviations(text)
    
    # Step 5: Handle currency and numbers
    text = handle_currency_and_numbers(text)
    
    # Step 6: Handle profanity censoring
    text = handle_profanity_censoring(text)
    
    # Step 7: Normalize punctuation
    text = normalize_punctuation(text)
    
    # Step 8: Add reading pauses
    text = add_reading_pauses(text)
    
    # Step 9: Improve sentence structure
    text = improve_sentence_structure(text)
    
    # Step 10: Clean whitespace
    text = clean_whitespace(text)
    
    # Optional: Add context words for quotes
    if include_context_words:
        text = re.sub(r'"([^"]+)"', r'quote \1 end quote', text)
    
    return text

def format_reddit_post_for_tts(post_dict):
    """
    Format a complete Reddit post dictionary for TTS.
    
    Args:
        post_dict (dict): Dictionary containing Reddit post data
    
    Returns:
        dict: Formatted post with TTS-ready text
    """
    if not isinstance(post_dict, dict):
        return post_dict
    
    formatted_post = post_dict.copy()
    
    # Format the main post content
    if 'submission_post' in post_dict:
        formatted_post['submission_post_tts'] = format_text_for_tts(post_dict['submission_post'])
    
    # Format the title if present
    if 'submission_title' in post_dict:
        formatted_post['submission_title_tts'] = format_text_for_tts(post_dict['submission_title'])
    
    return formatted_post