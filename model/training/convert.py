from PIL import Image
import pillow_heif
import os

# Register HEIC format
pillow_heif.register_heif_opener()

# Convert all HEIC files in current directory
input_folder = '.'  # Current directory
output_folder = '.'
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.heic'):
        heic_path = os.path.join(input_folder, filename)
        jpg_path = os.path.join(output_folder, filename.replace('.heic', '.jpg').replace('.HEIC', '.jpg'))
        
        print(f"Processing: {filename}")
        img = Image.open(heic_path)
        rgb_img = img.convert('RGB')
        rgb_img.save(jpg_path, 'JPEG', quality=95)
        
        # Verify the output file
        file_size = os.path.getsize(jpg_path)
        print(f"✓ Converted: {filename} → {jpg_path} ({file_size} bytes)")

print("✅ All images converted!")
