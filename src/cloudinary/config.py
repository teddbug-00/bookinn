from pydantic_settings import BaseSettings


class CloudinarySettings(BaseSettings):
    """Defines the configuration settings for the Cloudinary service."""
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str


cloudinary_settings = CloudinarySettings()
