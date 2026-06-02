# Quick Start Guide - VS Code Setup

Follow these steps to get your construction company website running in VS Code.

## Step 1: Extract the Project

Extract the `construction-company-site.tar.gz` file to your desired location on your computer.

## Step 2: Open in VS Code

1. Open VS Code
2. Click **File → Open Folder**
3. Select the `construction-company-site` folder
4. Click **Open**

## Step 3: Open Terminal in VS Code

1. Press `Ctrl + `` (backtick) to open the integrated terminal
2. Or go to **Terminal → New Terminal**

## Step 4: Create Virtual Environment

In the VS Code terminal, run:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Run the Application

```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

## Step 7: View Your Website

1. Open your web browser
2. Go to `http://localhost:5000`
3. You should see your construction company website!

## Step 8: Make Changes

Now you can edit files in VS Code:

- **Edit content**: Modify HTML files in the `templates/` folder
- **Change colors/styling**: Edit `static/css/style.css`
- **Add functionality**: Modify JavaScript files in `static/js/`
- **Update backend**: Edit `app.py`

### Pro Tips:

- **Auto-reload**: Flask automatically reloads when you save Python files
- **Hard refresh**: Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac) in browser to clear cache and see CSS changes
- **Debug mode**: Flask is running in debug mode, so you'll see errors in the terminal

## Step 9: Stop the Server

Press `Ctrl+C` in the terminal to stop the Flask development server.

## Customization Checklist

- [ ] Change company name from "BuildPro" to your company name
- [ ] Update contact information in footer and contact page
- [ ] Modify primary color (blue) to match your brand
- [ ] Update services to match your offerings
- [ ] Add your portfolio projects
- [ ] Replace placeholder images with your own
- [ ] Update social media links

## Common Issues

### Port 5000 Already in Use

Edit `app.py` and change the port:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

### CSS Not Updating

Press `Ctrl+Shift+Delete` to clear browser cache, then refresh.

### Module Not Found Error

Make sure your virtual environment is activated (you should see `(venv)` in terminal).

## Next Steps

1. **Customize content** for your construction company
2. **Add real images** to replace emoji placeholders
3. **Set up email** for contact form submissions
4. **Deploy online** when ready (see README.md for deployment options)

---

**Need help?** Check the README.md file for detailed documentation.
