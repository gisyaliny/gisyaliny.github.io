# Website Maintenance Guide

This website is now powered by **Jekyll** and hosted on **GitHub Pages**. Content is managed via simple configuration files in the `_data/` folder, separating content from code.

## 📁 Project Structure

```
├── _config.yml         # Main site configuration (Title, Author, Google Scholar ID)
├── _data/              # Content data files
│   ├── publications.yml
│   ├── research.yml
│   ├── teaching.yml
│   ├── awards.yml
│   ├── education.yml
│   └── experience.yml
├── index.html          # Main homepage template
├── cv.html             # CV template (auto-generated from data)
├── scripts/            # Automation scripts
└── archive/            # Old scripts
```

## 📝 How to Update Content

You do **not** need to touch `index.html` or `cv.html` to add new content. Just edit the YAML files in `_data/`.

### 1. Update Publications (Automated)
You can automatically fetch your latest papers from Google Scholar.

**Prerequisites:**
1. Install Python.
2. Install the `scholarly` package: `pip install scholarly PyYAML`.

**Usage:**
Run the script from the root of your repository:
```bash
python scripts/update_from_scholar.py
```
This will fetch your publications and overwrite `_data/publications.yml`.

### 2. Update Research, Awards, Teaching
Simply edit the corresponding YAML files in `_data/`.

### 3. Update CV
The CV is now automatically generated from:
- `_data/education.yml`
- `_data/experience.yml`
- `_data/publications.yml`
- `_data/awards.yml`
- `_config.yml` (Personal info)

Edit these files, and the CV page will update automatically.

## 🚀 How to Publish
1. Edit the files on your computer.
2. Push the changes to GitHub.
   ```bash
   git add .
   git commit -m "Update content"
   git push origin main
   ```
3. GitHub Pages will automatically rebuild and deploy your site within a few minutes.
