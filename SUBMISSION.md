# Publish and submit without losing history

The required submission is **one public GitHub repository URL**. This ZIP is the preparation package, not the final submission. Do not upload only the ZIP or bundle to GitHub: the source files and commits must be directly browsable.

## 1. Restore the repository

Extract the downloaded ZIP. In the extracted folder containing `visitor-photo-slideshow.bundle`, open PowerShell:

```powershell
git clone visitor-photo-slideshow.bundle visitor-photo-slideshow
```

Then enter the clone:

```powershell
cd visitor-photo-slideshow
git log --oneline
```

The bundle preserves the original development commits and subsequent review fixes, including authorship. It is not a fabricated or backdated history. Do not squash these commits. The clone is the project folder to run and publish; a source copy is also included for easy inspection.

## 2. Check the app

Follow README.md to install dependencies and run the app. Run `python -m unittest -v` using your virtual environment. Complete the pending manual checks in TEST_RESULTS.md. Read DEMO_GUIDE.md and explain the code in your own words. Add your own genuine refinements as new commits when you make them.

## 3. Create the destination

On GitHub, create a repository named `visitor-photo-slideshow`. Select **Public**. Leave the options to add a README, .gitignore and license unchecked, because the local repository already has its files and history. Use the exact HTTPS URL GitHub gives you.

The bundle clone's origin initially points to a local file. Change it and push:

```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/visitor-photo-slideshow.git
git push -u origin main
```

Replace YOUR_USERNAME with your actual GitHub username. Authenticate using your usual GitHub sign-in or GitHub Desktop; never put credentials into project files. In GitHub Desktop, you can add the restored local repository instead of creating a new repository from the source copy.

## 4. Verify and submit

Open the repository link in an incognito/logged-out window. Confirm it loads without login, the root shows all required Markdown files and app source, and the Commits page shows the preserved history. Check no event database, visitor photos, `.env`, or credentials were uploaded.

Submit that repository URL. A deployed app URL is optional; this app can be demonstrated locally. Do not use GitHub Pages to run the Python backend.
