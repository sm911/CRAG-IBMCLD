# Script to commit and push changes to both GitHub and GitLab

# Prompt for commit message
$commitMessage = Read-Host "Enter commit message"

# Add all changes to staging
git add .

# Commit changes
git commit -m "$commitMessage"

# Push to GitHub
Write-Host "Pushing to GitHub..."
git push origin master

# Push to GitLab
Write-Host "Pushing to GitLab..."
git push gitlab master

Write-Host "Push to both GitHub and GitLab completed!"
