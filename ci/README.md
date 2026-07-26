# CI configuration

`github-workflow-tests.yml` is a ready-to-use GitHub Actions workflow: it runs the
test suite and separately re-validates the knowledge base (so a corrupt rule file
fails the build instead of reaching a student).

**It lives here rather than in `.github/workflows/` because the token used to push
this branch lacks GitHub's `workflow` scope** — an authorisation limit, not a
problem with the file. To activate it:

```bash
mkdir -p .github/workflows
git mv ci/github-workflow-tests.yml .github/workflows/tests.yml
git commit -m "Enable CI" && git push
```

Anyone pushing with normal repo permissions can do this in one commit.
