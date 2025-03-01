import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FAL_KEY = os.getenv("FAL_API_KEY", "your-api-key")  # Replace with actual API key
    FAL_TRAIN_URL = "https://queue.fal.run/fal-ai/flux-lora-portrait-trainer"
    FAL_STATUS_URL = "https://queue.fal.run/fal-ai/flux-lora-portrait-trainer/requests"
    FAL_RESULT_URL = "https://queue.fal.run/fal-ai/flux-lora-portrait-trainer/requests"
    FAL_GENERATE_URL = "https://queue.fal.run/fal-ai/flux-lora"
    FAL_RESULT_IMAGE_URL = "https://queue.fal.run/fal-ai/flux-lora/requests"
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
