# Vision Analyzer Skill

Analyze images using vision-capable models (NVIDIA VLM, GPT-4V, Claude Vision).

## Capabilities

- **Image Description**: Generate detailed descriptions of images
- **Object Detection**: Identify objects, people, text in images
- **OCR**: Extract text from images, documents, screenshots
- **Scene Analysis**: Understand context, activities, relationships
- **Document Analysis**: Parse forms, receipts, invoices, contracts
- **Screenshot Analysis**: Analyze UI elements, errors, layouts

## Usage

```bash
# Analyze an image
openclaw skills run vision-analyzer --image /path/to/image.jpg

# Extract text (OCR)
openclaw skills run vision-analyzer --image /path/to/doc.jpg --task ocr

# Describe image
openclaw skills run vision-analyzer --image /path/to/photo.jpg --task describe

# Detect objects
openclaw skills run vision-analyzer --image /path/to/scene.jpg --task objects
```

## Configuration

Add to `openclaw.json`:

```json
{
  "vision": {
    "provider": "nvidia",  // or "openai", "anthropic", "google"
    "model": "nvidia/vila-34b",
    "apiKey": "${VISION_API_KEY}"
  }
}
```

## Requirements

- Pillow (PIL)
- requests
- Vision-capable model API key

## Examples

### Describe Image
```python
from vision_analyzer import analyze

result = analyze("/path/to/image.jpg", task="describe")
print(result.description)
```

### Extract Text (OCR)
```python
result = analyze("/path/to/document.jpg", task="ocr")
print(result.text)
```

### Detect Objects
```python
result = analyze("/path/to/scene.jpg", task="objects")
print(result.objects)  # List of detected objects with bounding boxes
```

## Integration

This skill integrates with:
- Revenue Recovery (analyze invoices, receipts)
- Contract Parser (scan signed documents)
- Executive Briefing (include charts/graphs analysis)
- Self-healing (analyze error screenshots)

## API

```python
def analyze_image(
    image_path: str,
    task: str = "describe",
    model: str = "default",
    detailed: bool = True
) -> AnalysisResult:
    """
    Analyze an image using vision models.
    
    Args:
        image_path: Path to image file
        task: One of: describe, ocr, objects, scene, document
        model: Model to use (default from config)
        detailed: Include detailed analysis
    
    Returns:
        AnalysisResult with description, text, objects, etc.
    """
```

## Security

- Images processed locally before upload
- No permanent storage of analyzed images
- API keys from environment only
- Supports on-prem vision models

## See Also

- `contract-parser` - For document parsing
- `financial-telemetry` - For invoice/receipt processing
- `meta-healing` - For screenshot analysis
