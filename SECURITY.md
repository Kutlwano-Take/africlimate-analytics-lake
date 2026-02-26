# Security Guide

## Secrets Policy
- Never commit real credentials, tokens, private keys, or `.env` files with real values.
- Store secrets only in environment variables (Render dashboard, local machine secret store).
- Use `.env.example` only as a placeholder template.

## Pre-Push Checklist
1. Run secret scan:
```bash
rg -n --hidden -g "!.git" -e "AKIA[0-9A-Z]{16}" -e "ASIA[0-9A-Z]{16}" -e "ghp_[A-Za-z0-9]{36}" -e "github_pat_[A-Za-z0-9_]{20,}" -e "-----BEGIN (RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----" -e "AWS_SECRET_ACCESS_KEY\\s*=\\s*[A-Za-z0-9/+=]{20,}" .
```
2. Verify tracked files:
```bash
git ls-files
```
3. Confirm no local env files are staged:
```bash
git status --short
```

## If a Secret Is Exposed
1. Revoke/rotate the credential immediately (AWS IAM, GitHub token, etc.).
2. Remove the secret from files and commit.
3. If already pushed, rewrite history and force-push only if required by policy.
4. Redeploy with fresh credentials.

## Runtime Hardening
- Keep `DASH_DEBUG_MODE=false` in production.
- Prefer `FORCE_FALLBACK_DATA=true` for demos/submission stability.
- Restrict AWS IAM permissions to least privilege.
