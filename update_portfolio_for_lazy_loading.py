
import re

file_path = '/home/ubuntu/seiso-construction-site/templates/portfolio.html'

with open(file_path, 'r') as f:
    content = f.read()

# Regex to find img tags with src pointing to images_optimized or images_thumbnails
# and capture the filename. This regex is more general to catch existing states.
img_tag_regex = re.compile(
    r'(<img\s+src=\"{{\s*url_for\([\\\'\"]static[\\\'\"]\s*,\s*filename=[\\\'\"](?:images_optimized|images_thumbnails)/([^\\\'\"]+?)[\\\'\"]\)\s*}}\")([^>]*?)>'
)

# Function to replace and add data-src
def replace_img_tag(match):
    full_src_attr = match.group(1) # e.g., src="{{ url_for('static', filename='images_optimized/foo.jpeg') }}"
    filename = match.group(2)
    other_attrs = match.group(3)

    # Construct the new src and data-src attributes
    new_src = f"src=\\\"{{{{ url_for(\'static\', filename=\'images_thumbnails/{filename}\') }}}}\\\""
    new_data_src = f"data-src=\\\"{{{{ url_for(\'static\', filename=\'images_optimized/{filename}\') }}}}\\\""

    # Ensure loading="lazy" is present
    if 'loading="lazy"' not in other_attrs:
        other_attrs += ' loading="lazy"'

    # Remove any existing src and data-src to rebuild them correctly
    other_attrs = re.sub(r'src=\"[^\"]*\"', '', other_attrs)
    other_attrs = re.sub(r'data-src=\"[^\"]*\"', '', other_attrs)

    return f'<img {new_src} {new_data_src}{other_attrs}>'

# Apply replacements for img tags
new_content = img_tag_regex.sub(replace_img_tag, content)

# Regex to find href attributes pointing to images_thumbnails and change to images_optimized
href_thumbnail_regex = re.compile(
    r'(<a\s+href=\"{{\s*url_for\([\\\'\"]static[\\\'\"]\s*,\s*filename=[\\\'\"]images_thumbnails/([^\\\'\"]+?)[\\\'\"]\)\s*}}\")([^>]*?)>'
)

def replace_href_thumbnail(match):
    filename = match.group(2)
    other_attrs = match.group(3)
    new_href = f"href=\\\"{{{{ url_for(\'static\', filename=\'images_optimized/{filename}\') }}}}\\\""
    return f'<a {new_href}{other_attrs}>'

# Apply replacements for href attributes
new_content = href_thumbnail_regex.sub(replace_href_thumbnail, new_content)

with open(file_path, 'w') as f:
    f.write(new_content)

print("portfolio.html updated for lazy loading.")
