import re

def fix_jinja_syntax(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Regex to find src attributes with missing closing curly brace
    # It looks for `src="{{ url_for('static', filename='...') }"` and replaces it with `src="{{ url_for('static', filename='...') }}"`
    content = re.sub(r"(src=\"{{\s*url_for\(\\'static\\',\s*filename=\\'[^\\']+\\'\)\s*)\"(?!}}})", r"\1}}", content)

    # Regex to find data-src attributes with missing closing curly brace
    # It looks for `data-src="{{ url_for('static', filename='...') }"` and replaces it with `data-src="{{ url_for('static', filename='...') }}"`
    content = re.sub(r"(data-src=\"{{\s*url_for\(\\'static\\',\s*filename=\\'[^\\']+\\'\)\s*)\"(?!}}})", r"\1}}", content)

    with open(file_path, 'w') as f:
        f.write(content)

    print("Jinja2 syntax fixed in portfolio.html")

if __name__ == '__main__':
    fix_jinja_syntax('/home/ubuntu/seiso-construction-site/templates/portfolio.html')
