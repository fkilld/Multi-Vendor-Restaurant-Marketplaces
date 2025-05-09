from django.core.exceptions import ValidationError
import os


def allow_only_images_validator(value):
    """
    Validator to ensure only image files are uploaded.
    
    Flow:
    1. Extract file extension from the uploaded file
    2. Define list of valid image extensions
    3. Check if the file extension is valid
    4. If not valid, raise ValidationError
    """
    
    # Extract the file extension from the uploaded file name
    # For example, from 'cover-image.jpg', it extracts '.jpg'
    ext = os.path.splitext(value.name)[1]
    print(ext)
    
    # Define a list of valid image file extensions
    valid_extensions = ['.png', '.jpg', '.jpeg']
    
    # Check if the extracted extension is in our list of valid extensions
    # Convert to lowercase to ensure case-insensitive comparison
    if not ext.lower() in valid_extensions:
        # If the extension is not valid, raise a ValidationError with
        # a descriptive message showing allowed extensions
        raise ValidationError('Unsupported file extension. Allowed extensions: ' +str(valid_extensions))