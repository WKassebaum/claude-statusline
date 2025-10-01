#!/usr/bin/env python3
"""
Test script to verify Sonnet 4.5 model name detection
"""

def test_model_detection(model_id):
    """Test the model detection logic"""
    model = "Claude"  # Default
    model_id_lower = model_id.lower()

    if 'opus-4-1' in model_id_lower or 'opus 4.1' in model_id_lower:
        model = "Opus 4.1"
    elif 'opus-4' in model_id_lower or 'opus 4' in model_id_lower:
        model = "Opus 4"
    elif 'sonnet-4-5' in model_id_lower or 'sonnet 4.5' in model_id_lower:
        model = "Sonnet 4.5"
    elif 'sonnet-4' in model_id_lower or 'sonnet 4' in model_id_lower:
        model = "Sonnet 4"
    elif 'sonnet-3-5' in model_id_lower or 'sonnet 3.5' in model_id_lower or 'sonnet-20241022' in model_id_lower:
        model = "Sonnet 3.5"
    elif 'sonnet' in model_id_lower:
        model = "Sonnet"
    elif 'haiku' in model_id_lower:
        model = "Haiku"

    return model

# Test cases
test_cases = [
    ("claude-sonnet-4-5-20250929", "Sonnet 4.5"),
    ("claude-sonnet-4-5", "Sonnet 4.5"),
    ("claude-sonnet-4-20241022", "Sonnet 4"),
    ("claude-sonnet-4", "Sonnet 4"),
    ("claude-sonnet-3-5-20241022", "Sonnet 3.5"),
    ("claude-opus-4-1-20250805", "Opus 4.1"),
    ("claude-opus-4-20241022", "Opus 4"),
    ("claude-3-haiku-20240307", "Haiku"),
]

print("Testing Model Name Detection")
print("=" * 60)

all_passed = True
for model_id, expected in test_cases:
    result = test_model_detection(model_id)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    if result != expected:
        all_passed = False
    print(f"{status} | {model_id:40s} → {result:15s} (expected: {expected})")

print("=" * 60)
if all_passed:
    print("✅ All tests passed!")
else:
    print("❌ Some tests failed!")

exit(0 if all_passed else 1)
