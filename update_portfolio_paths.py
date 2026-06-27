import re

# Read the portfolio.html file
with open('/home/ubuntu/seiso-construction-site/templates/portfolio.html', 'r') as f:
    content = f.read()

# Replace all image_compressed paths with images_optimized paths
content = content.replace('images_compressed/', 'images_optimized/')

# Replace all src attributes to use thumbnails instead
# Pattern: src="{{ url_for('static', filename='images_optimized/...') }}"
# Replace with: src="{{ url_for('static', filename='images_thumbnails/...') }}" data-src="{{ url_for('static', filename='images_optimized/...') }}"

def replace_src_with_thumbnail(match):
    full_match = match.group(0)
    filename = match.group(1)
    return f'src="{{{{ url_for("static", filename="images_thumbnails/{filename}") }}}}" data-src="{{{{ url_for("static", filename="images_optimized/{filename}") }}}}"'

# Pattern to match src attributes with images_optimized
pattern = r'src="\{\{ url_for\("static", filename="images_optimized/([^"]+)"\) \}\}"'
content = re.sub(pattern, replace_src_with_thumbnail, content)

# Write the updated content back
with open('/home/ubuntu/seiso-construction-site/templates/portfolio.html', 'w') as f:
    f.write(content)

print("Updated portfolio.html with optimized image paths and thumbnails")
