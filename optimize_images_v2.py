import os
from PIL import Image

def optimize_images(input_dir, output_dir, thumbnail_dir, quality=60, max_width=1200, thumb_width=300):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            try:
                img_path = os.path.join(input_dir, filename)
                img = Image.open(img_path)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Optimize main image
                width_percent = (max_width / float(img.size[0]))
                if width_percent < 1:
                    new_height = int((float(img.size[1]) * float(width_percent)))
                    img_resized = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                else:
                    img_resized = img
                
                output_path = os.path.join(output_dir, filename)
                img_resized.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                # Create small thumbnail for lazy loading
                thumb_percent = (thumb_width / float(img.size[0]))
                thumb_height = int((float(img.size[1]) * float(thumb_percent)))
                img_thumb = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                
                thumb_path = os.path.join(thumbnail_dir, filename)
                img_thumb.save(thumb_path, 'JPEG', quality=30, optimize=True)
                
                print(f"Optimized: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    base_static = "/home/ubuntu/seiso-construction-site/static"
    input_images = os.path.join(base_static, "images")
    output_images = os.path.join(base_static, "images_optimized")
    thumbnail_images = os.path.join(base_static, "images_thumbnails")
    
    optimize_images(input_images, output_images, thumbnail_images)
