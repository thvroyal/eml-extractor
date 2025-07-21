# GitHub Workflows Setup Instructions

This document provides step-by-step instructions for setting up automated publishing and testing for your EML Parser library using GitHub Actions.

## Overview

The repository includes three main GitHub Actions workflows:

1. **`test.yml`** - Runs tests on every push and pull request
2. **`publish.yml`** - Automatically publishes to PyPI on releases
3. **`release.yml`** - Creates GitHub releases when you push version tags

## Step 1: PyPI API Tokens Setup

### 1.1 Create PyPI Account
1. Go to [PyPI.org](https://pypi.org) and create an account
2. Verify your email address

### 1.2 Create Test PyPI Account (Optional but Recommended)
1. Go to [Test PyPI](https://test.pypi.org) and create an account
2. This allows you to test publishing without affecting the real PyPI

### 1.3 Generate API Tokens

#### For PyPI:
1. Log in to [PyPI.org](https://pypi.org)
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Give it a name (e.g., "GitHub Actions EML Parser")
5. Choose scope: "Entire account" (you can restrict this later after first publish)
6. Copy the token (starts with `pypi-`)

#### For Test PyPI:
1. Log in to [Test PyPI](https://test.pypi.org)
2. Repeat the same steps as above
3. Copy the token

### 1.4 Add Tokens to GitHub Secrets
1. Go to your GitHub repository
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:
   - Name: `PYPI_API_TOKEN`, Value: your PyPI token
   - Name: `TEST_PYPI_API_TOKEN`, Value: your Test PyPI token

## Step 2: Repository Setup

### 2.1 Branch Protection (Optional but Recommended)
1. Go to Settings → Branches
2. Add a rule for your main branch (usually `main` or `master`)
3. Enable:
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include the test workflow checks

### 2.2 Create Initial Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: EML Parser library"

# Add remote and push
git remote add origin https://github.com/yourusername/eml-parser.git
git branch -M main
git push -u origin main
```

## Step 3: Testing the Workflows

### 3.1 Test the Test Workflow
1. Make any small change to the code
2. Commit and push to main branch
3. Check the "Actions" tab in GitHub to see the tests running

### 3.2 Test Publishing to Test PyPI
1. Go to Actions tab in GitHub
2. Click on "Build and Publish to PyPI" workflow
3. Click "Run workflow"
4. Leave "Publish to Test PyPI" checked
5. Click "Run workflow"
6. This will build and publish to Test PyPI

## Step 4: Publishing Your First Release

### 4.1 Update Version Number
First, make sure your version number is correct in:
- `eml_parser/__init__.py` 
- `setup.py`
- `pyproject.toml`

### 4.2 Create and Push a Version Tag
```bash
# Create a version tag
git tag v1.0.0

# Push the tag
git push origin v1.0.0
```

### 4.3 Create GitHub Release
1. The `release.yml` workflow will automatically create a GitHub release
2. Alternatively, you can create it manually:
   - Go to Releases → Create a new release
   - Choose the tag you just created
   - Add release notes
   - Click "Publish release"

### 4.4 Automatic PyPI Publishing
Once you publish the GitHub release, the `publish.yml` workflow will:
1. Run all tests
2. Build the package
3. Publish to PyPI automatically

## Step 5: Ongoing Maintenance

### 5.1 Making New Releases
For subsequent releases:

1. **Update version numbers** in all relevant files
2. **Commit changes**:
   ```bash
   git add .
   git commit -m "Bump version to v1.1.0"
   git push
   ```
3. **Create and push tag**:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
4. **Create GitHub release** (triggers automatic PyPI publishing)

### 5.2 Pre-release Versions
For alpha, beta, or release candidate versions:
```bash
git tag v1.1.0-alpha.1
git tag v1.1.0-beta.1
git tag v1.1.0-rc.1
```
These will be marked as pre-releases automatically.

## Step 6: Troubleshooting

### 6.1 Common Issues

**Publishing Fails:**
- Check that API tokens are correctly set in GitHub secrets
- Ensure version number hasn't been used before
- Check that all tests pass

**Tests Fail:**
- Review the test output in the Actions tab
- Test locally with: `pytest tests/`
- Ensure all dependencies are properly specified

**Import Errors:**
- Verify package structure is correct
- Check `__init__.py` exports
- Test locally with: `pip install -e .`

### 6.2 Manual Publishing (Fallback)
If automatic publishing fails, you can publish manually:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Step 7: Security Best Practices

1. **Use scoped API tokens**: After first publish, create project-specific tokens
2. **Regularly rotate tokens**: Update API tokens periodically
3. **Monitor releases**: Set up notifications for new releases
4. **Review dependencies**: Keep dependencies updated and secure

## Step 8: Additional Workflows (Optional)

### 8.1 Dependabot for Dependency Updates
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 8.2 CodeQL Security Analysis
Add to your workflows or enable in Security tab:
```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v2
  with:
    languages: python
```

## Support

If you encounter issues:
1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review the [PyPI publishing guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
3. Open an issue in this repository

## Summary

Once set up, your workflow will be:
1. **Develop** → Push changes → Tests run automatically
2. **Ready to release** → Update version → Create tag → Push tag
3. **Create GitHub release** → Package automatically published to PyPI

This provides a professional, automated release process for your Python library! 