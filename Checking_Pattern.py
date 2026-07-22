import re

# Regex patterns
# Add anchors to ensure the entire string matches
strict_pattern = r'^([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})$'
relaxed_pattern = r'^\s*([A-Z0-9]\s*[A-Z0-9]\s*[A-Z0-9]\s*[A-Z0-9])\s*-\s*([A-Z0-9]\s*[A-Z0-9]\s*[A-Z0-9]\s*[A-Z0-9])\s*-\s*([A-Z0-9]\s*[A-Z0-9]\s*[A-Z0-9]\s*[A-Z0-9])\s*$'

# Or use re.fullmatch instead:

    # rest of code

# Test samples with more varied cases
samples = [
    "1234-ABCD-5678",             # Perfect
    "123 4-ABCD-5678",            # Space in first part
    "1234 -ABCD-5678",            # Space before hyphen
    "1234- ABCD-5678",            # Space after hyphen
    "1234-ABCD -5678",            # Space before second hyphen
    "1234-ABCD- 5678",            # Space after second hyphen
    "1234-ABCD-5678 ",            # Space at the end
    " 1234-ABCD-5678",            # Space at the beginning
    "12X4-AB1D-5678",             # Valid
    "12-ABCD-5678",               # Invalid, first part too short
    "1234-ABCDE-5678",            # Invalid, second part too long
    "1 2 3 4 - A B C D - 5 6 7 8", # Spaces between all characters
    "  1234  -  ABCD  -  5678  ", # Multiple spaces around hyphens
    "1 2 3 4-A B CD-4F3C",        # Mixed spaces
    "12 34-A BCD-56 78",          # Different space positions
    "1234-ABC D-5678",            # Space in middle of group
    "12 34 - AB CD - 56 78",      # Consistent spaces
    "1234-ABCD-567",              # Invalid, third part too short
    "12345-ABCD-5678",            # Invalid, first part too long
    "A1-B2-C3",                   # Invalid, all parts too short
    "A1 B2-C3 D4-E5 F6"           # Valid with spacing pattern
]

print("\n=== Testing Strict Pattern ===\n")
for text in samples:
    match = re.fullmatch(strict_pattern, text)
    if match:
        print(f"✅ Matched: {match.group(1)}    | Text: '{text}'")
    else:
        print(f"❌ No Match                     | Text: '{text}'")


print("\n=== Testing Relaxed Pattern (spaces allowed) ===\n")
for text in samples:
    match = re.fullmatch(relaxed_pattern, text)
    if match:
        combined = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        print(f"✅ Matched: {combined}    | Text: '{text}'")
    else:
        print(f"❌ No Match                     | Text: '{text}'")