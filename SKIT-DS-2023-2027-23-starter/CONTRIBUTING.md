# Team contribution workflow

1. Update your local `main` branch before starting.
2. Create your personal branch, e.g. `sandeep/audio-preprocessing`.
3. Make small, genuine changes and test them.
4. Commit with a clear message, e.g. `feat: add WAV file validation`.
5. Push your branch and open a pull request to `main`.
6. Ask a teammate to review; merge after checks pass.
7. Pull the updated `main` before starting the next task.

Set your Git identity on your own machine (replace with your own GitHub-linked email):
```bash
git config --global user.name "Your Name"
git config --global user.email "your-verified-github-email@example.com"
git config --get user.name
git config --get user.email
```

Do not set every member's Git identity to the same name/email. Never make commits on behalf of another member.
