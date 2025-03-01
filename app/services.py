from flask import request, jsonify
import fal_client
from werkzeug.utils import secure_filename
import openai
import random
import builtins
import os
from app.routes import train_lora, check_status, get_result, generate_image,generate_image_result
from supabase import create_client
from app.config import Config

def disable_print():
    """Redirects print statements to a dummy function."""
    builtins.print = lambda *args, **kwargs: None

# Disable print in production
disable_print()

print(f"Supabase URL: {Config.SUPABASE_URL}")  # Debugging line
print(f"Supabase Key: {Config.SUPABASE_KEY}")  # Debugging line
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def insert_training_request(request_id, user_name, trigger_phrase):
    """Insert training request details into Supabase."""
    data = {
        "request_id": request_id,
        "user_name": user_name,
        "trigger_phrase": trigger_phrase,
        "status": "In_Queue"
    }
    response = supabase.table("training_requests").insert(data).execute()
    return response

def update_training_status(request_id, new_status, new_completion_percentage):
    """Update training status & completion percentage in Supabase only if changed."""
    
    # Fetch existing data from Supabase
    existing_entry = supabase.table("training_requests").select("status", "completion_percentage") \
        .eq("request_id", request_id).execute()

    if existing_entry.data:
        current_status = existing_entry.data[0]["status"]
        current_completion = existing_entry.data[0]["completion_percentage"]

        # Update only if status or completion percentage has changed
        update_data = {}

        if current_status != new_status:
            update_data["status"] = new_status
        if current_completion != new_completion_percentage:
            update_data["completion_percentage"] = new_completion_percentage

        if update_data:
            response = supabase.table("training_requests") \
                .update(update_data) \
                .eq("request_id", request_id) \
                .execute()
            print("Supabase Updated:", response)
            return response
    return None

def update_safe_tensors(request_id, safe_tensors):
    """Update safe_tensors column in Supabase."""
    print('update_sensors',safe_tensors)
    response = supabase.table("training_requests") \
        .update({"safe_tensors": safe_tensors}) \
        .eq("request_id", request_id) \
        .execute()

    return response

def insert_initial_request(request_id, prompt,image_no):
    """Insert request_id, prompt, and status='IN_PROGRESS' into Supabase."""
    data = {
        "request_id": request_id,
        "prompt": prompt,
        "image": image_no,
        "status": "IN_PROGRESS"  # Set initial status
    }
    response = supabase.table("results").insert(data).execute()
    print("Inserted initial request into Supabase:", response)

def update_generated_image(request_id, image_url, width, height,image_no):
    """Update the generated_images table with image details after generation."""
    data = {
        "image_url": image_url,
        "width": width,
        "height": height,
        "status": "COMPLETED"  # Update status to COMPLETED
    }
    response = supabase.table("results") \
        .update(data) \
        .eq("request_id", request_id) \
        .eq("image", image_no) \
        .execute()
    print("Updated generated image details in Supabase:", response)
    
def insert_trigger_phrase_naturally(generated_prompt, trigger_phrase):
    """Insert trigger_phrase at the beginning or middle in a meaningful way."""
    words = generated_prompt.split()

    if trigger_phrase.lower() in generated_prompt.lower():
        return generated_prompt  # ✅ Already included, no need to modify

    # Insert at the beginning (50% chance) or middle (50% chance)
    insert_position = 0 if random.choice([True, False]) else len(words) // 2
    
    words.insert(insert_position, trigger_phrase)
    
    # Ensure natural sentence structure
    improved_prompt = " ".join(words)
    
    return improved_prompt

def generate_gpt4o_prompt(youtube_title,trigger_phrase,gender_type):
    """Generate a detailed YouTube thumbnail prompt using GPT-4o."""
    
    client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    try:
        
        gender_instruction = {
            "Male": "Generate a highly detailed image prompt featuring a confident, charismatic male character.",
            "Female": "Generate a highly detailed image prompt featuring a strong, powerful female character.",
            "General": "Generate a highly detailed gender-neutral image prompt suitable for all audiences."
        }

        # ✅ Select the correct instruction based on `gender_type`
        gender_context = gender_instruction.get(gender_type, gender_instruction["General"])
        
        print('gender_context',gender_context)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "Act as an expert copywriter. Your task is to generate a highly detailed, engaging prompt for a YouTube thumbnail "
                    "based on the topic {youtube_title}. The generated prompt should strictly include the keyword {trigger_phrase} "
                    "within the description."
                    "\n\n STRICT RULES:  "
                    "\n The character's gender **must strictly follow** the provided parameter: {gender_type}.\n"
                    "\n Generate a highly detailed image description in a natural storytelling format."
                    "\n DO NOT explicitly mention categories like 'Physical Traits,' 'Pose,' or 'Lighting.'"
                    "\n DO NOT include any text in the thumbnail."
                    "\n Ensure seamless integration of all seven critical elements."
                    "\n\n Mandatory Elements to Include (Use Examples Below for Reference):**"
                    "\n\n 1. Physical Traits - Describe defining characteristics naturally."
                    "\n   - Example: 'A middle-aged businessman with a sharp gaze and strong facial features.'"
                    "\n   - Example: 'A young woman with long, flowing red hair and bright blue eyes, exuding confidence.'"
                    "\n   - Example: 'A muscular warrior with a thick beard and battle scars, wearing ancient armor.'"
                    "\n\n 2. Pose - Specify body positioning in an immersive way."
                    "\n   - Example: 'Standing with arms crossed, exuding confidence and authority.'"
                    "\n   - Example: 'Leaning slightly forward with one hand on the table, as if making an important decision.'"
                    "\n\n 3. Expression - Define facial emotion to match the scene's mood."
                    "\n   - Example: 'A deep, intense stare, eyebrows slightly furrowed, lips pressed together.'"
                    "\n   - Example: 'Eyebrows raised, head slightly tilted, lips parted as if about to ask a question.'"
                    "\n\n 4. Background - Provide a compelling setting for context."
                    "\n   - Example: 'A futuristic cyberpunk city at night, glowing neon signs and flying cars in the distance.'"
                    "\n   - Example: 'A dark, moody office with a single desk lamp illuminating a stack of documents.'"
                    "\n\n 5. Lighting - Describe how light interacts with the subject."
                    "\n   - Example: 'A warm, golden glow softly highlighting the subject’s face, with subtle shadows for depth.'"
                    "\n   - Example: 'Deep blue and red neon lights casting dramatic shadows.'"
                    "\n\n 6. Details - Add hyperrealistic elements to enhance realism."
                    "\n   - Example: 'Hyperrealistic skin texture, with visible pores and slight imperfections.'"
                    "\n\n 7. Equipment - Specify virtual camera settings for a professional look."
                    "\n   - Example: 'Shot with a Canon EOS R5, 50mm f/1.2 lens.'"
                    "\n\n Your final output must smoothly integrate all these elements into a realistic, engaging scene description."
                )},
                {"role": "user", "content": f"Generate a YouTube thumbnail prompt for the topic: {youtube_title}"}
            ],
            temperature=0.7
        )
        
        generated_prompt = response.choices[0].message.content.strip()
        improved_prompt = insert_trigger_phrase_naturally(generated_prompt, trigger_phrase)
        return improved_prompt
    except Exception as e:
        print(f"❌ GPT-4o Error: {e}")
        return youtube_title  # ✅ Fallback to the original title if GPT fails

def get_trigger_phrase(request_id):
    """Fetch trigger_phrase from the training_requests table using request_id."""
    try:
        response = supabase.table("training_requests") \
            .select("trigger_phrase") \
            .eq("request_id", request_id) \
            .limit(1) \
            .execute()

        if response.data:
            return response.data[0].get("trigger_phrase")
        else:
            print(f"❌ No trigger_phrase found for request_id: {request_id}")
            return None  # Return None if not found
    except Exception as e:
        print(f"❌ Error fetching trigger_phrase: {e}")
        return None

def setup_routes(app):
    
    #Create the uploads folder if it doesn't exist
    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created folder: {UPLOAD_FOLDER}")

    ALLOWED_EXTENSIONS = {"zip"}

    def allowed_file(filename):
        """Check if the uploaded file is a ZIP file."""
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/train', methods=['POST'])
    def train():
        
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        trigger_phrase = request.form.get("trigger_phrase", "reva")
        user_name = request.form.get("user_name", "unknown_user")  # Get user name from frontend

        if file.filename == "" or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only .zip allowed"}), 400

        # Secure and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        file = request.files["file"]
        trigger_phrase = request.form.get("trigger_phrase", "reva")
        images_data_url = fal_client.upload_file(file_path)
        

        if not images_data_url:
            return jsonify({"error": "images_data_url is required"}), 400

        result = train_lora(images_data_url, trigger_phrase)
        if result:        
            request_id = result.get("request_id")
            # Insert training details into Supabase
            insert_response = insert_training_request(request_id, user_name, trigger_phrase)
            print("Inserted into Supabase:", insert_response)
            return jsonify({"message": "Training started", "request_id": result.get("request_id")}), 202
        else:
            return jsonify({"error": "Training failed"}), 500

    @app.route('/status/<request_id>', methods=['GET'])
    def status(request_id):
        """Check training status from Fal.ai, update status & completion in Supabase."""
        result = check_status(request_id)

        if result:
            # Extract status & completion percentage from Fal.ai response
            new_status = result.get("status", "unknown")
            
            completion_percentage = result["logs"][-1]["message"] if result.get("logs") else "0%"
            if new_status == "COMPLETED":
                completion_percentage = "100%"
                result_json = get_result(request_id)
                print('result_json',result_json)
                safe_tensors = result_json.get("diffusers_lora_file", {}).get("url")
                update_safe_tensors(request_id, safe_tensors)
            
            print(f"Status: {new_status}, Completion: {completion_percentage}")

            # Update Supabase only if values have changed
            update_training_status(request_id, new_status, completion_percentage)

            return jsonify({
                "request_id": request_id,
                "status": new_status,
                "completion_percentage": completion_percentage
            }), 200

        else:
            return jsonify({"error": "Failed to fetch status"}), 500

    @app.route('/generate_image', methods=['POST'])
    def generate():
        data = request.get_json()
        request_id = data.get("request_id")
        youtube_title = data.get("prompt")
        gender_type = data.get("gender")
        
        trigger_phrase = get_trigger_phrase(request_id)

        num_images = 2
        if not request_id or not youtube_title or not gender_type:
            return jsonify({"error": "request_id and youtube_title and gender_type are required"}), 400
        
        prompt = generate_gpt4o_prompt(youtube_title,trigger_phrase,gender_type)

        print('prompt_generated', prompt)
        print('trigger_phrase', trigger_phrase)
        
        result = generate_image(request_id, prompt)
        if result:
            request_id = result.get("request_id", "Request ID not found")
            
            for image_no in range(1, num_images + 1):
                insert_initial_request(request_id,prompt,image_no)
        else:
            return jsonify({"error": "Image generation failed"}), 500
        return jsonify(result) 
    
    @app.route('/insert_generated_images/<request_id>', methods=['GET'])
    def insert_generated_images(request_id):
        """Fetch generated images from Fal.ai and insert into Supabase."""
        response = generate_image_result(request_id)
        #print(response)
        if response:
            json_data = response

            # ✅ Extract image details
            images = json_data.get("images", [])
            prompt = json_data.get("prompt", "")

            for index, image in enumerate(images, start=1):
                image_url = image.get("url")
                width = image.get("width")
                height = image.get("height")

                # ✅ Insert into Supabase with status "COMPLETED"
                update_generated_image(request_id, image_url, width, height,image_no = index)

            return jsonify({"message": "Images inserted successfully", "request_id": request_id, "status": "COMPLETED"}), 200
        else:
            return jsonify({"details": response, "request_id": request_id}), 500

