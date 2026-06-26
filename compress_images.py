import os
from PIL import Image

def compress_images(input_dir, output_dir, quality=85):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            try:
                with Image.open(input_path) as img:
                    img.save(output_path, quality=quality, optimize=True)
                print(f"Compressed {filename}")
            except Exception as e:
                print(f"Error compressing {filename}: {e}")

if __name__ == "__main__":
    input_directory = "/home/ubuntu/seiso-construction-site/static/images"
    output_directory = "/home/ubuntu/seiso-construction-site/static/images_compressed"
    compress_images(input_directory, output_directory)
