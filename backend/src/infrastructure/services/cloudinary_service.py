import os

import cloudinary
import cloudinary.uploader


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True,
        )
        self.root_folder = os.getenv("CLOUDINARY_ROOT_FOLDER", "veterinaria.v2")

    def upload_document(self, file_bytes: bytes, company_id: str, entity_id: str, filename: str) -> dict:
        folder = f"{self.root_folder}/{company_id}/{entity_id}/docs"
        result = cloudinary.uploader.upload(
            file_bytes,
            folder=folder,
            public_id=filename,
            resource_type="raw",
            overwrite=False,
        )
        return {
            "public_id": result["public_id"],
            "secure_url": result["secure_url"],
        }
