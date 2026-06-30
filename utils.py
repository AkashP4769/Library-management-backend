

from pathlib import Path
import shutil

from litellm import uuid


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_image(image) -> str:
    """
    Save the uploaded image to the UPLOAD_DIR and return the image path.
    """
    extension = Path(image.filename).suffix
    
    filename = f"{uuid.uuid4()}{extension}"
    
    file_path = UPLOAD_DIR / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_path = f"/uploads/{filename}"

    return image_path