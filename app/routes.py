import requests
from app.config import Config

headers = {"Authorization": f"Key {Config.FAL_KEY}"}

def train_lora(images_data_url, trigger_phrase):
    payload = {
        "steps": 10,
        "subject_crop": True,
        "learning_rate": 0.00009,
        "trigger_phrase": trigger_phrase,
        "images_data_url": images_data_url,
        "multiresolution_training": True
    }
    response = requests.post(Config.FAL_TRAIN_URL, headers=headers, json=payload)
    return response.json() if response.status_code == 200 else None

def check_status(request_id):
    response = requests.get(f"{Config.FAL_STATUS_URL}/{request_id}/status?logs=1", headers=headers)
    return response.json() if response.status_code == 200 or response.status_code == 202 else None

def get_result(request_id):
    response = requests.get(f"{Config.FAL_RESULT_URL}/{request_id}", headers=headers)
    return response.json() if response.status_code == 200 else None

def generate_image(request_id, prompt):
    result = get_result(request_id)
    if not result or "diffusers_lora_file" not in result:
        return None

    lora_path = result.get("diffusers_lora_file", {}).get("url")
    payload = {
        "loras": [{"path": lora_path, "scale": 1}],
        "prompt": prompt,
        "embeddings": [],
        "image_size": "landscape_16_9",
        "model_name": None,
        "num_images": 2,
        "output_format": "jpeg",
        "enable_safety_checker": True
    }

    response = requests.post(Config.FAL_GENERATE_URL, headers=headers, json=payload)
    return response.json() if response.status_code == 200 else None

def generate_image_result(request_id):
    response = requests.get(f"{Config.FAL_RESULT_IMAGE_URL}/{request_id}", headers=headers)
    return response.json() if response.status_code == 200 else None