# Publishing to PyPI

Monolith publishes via **PyPI Trusted Publishing (OIDC)** — no long-lived API
token is stored in the repo. The workflow is `.github/workflows/publish.yml`; it
runs on every `v*` tag (which CI creates on merge to `master`).

## One-time setup

1. **Confirm the package name.** `pyproject.toml` uses `monolith-ai`. Make sure
   you own (or can claim) that name on PyPI.

2. **Create the GitHub environment.**
   Repo → Settings → Environments → **New environment** → name it `pypi`.
   (The publish job declares `environment: pypi`.)

3. **Add the Trusted Publisher on PyPI.**
   - Existing project: pypi.org → your project → **Manage → Publishing → Add a
     new pending publisher**.
   - Brand-new name: pypi.org → **Your projects → Publishing → Add a pending
     publisher**.

   Fill in:
   | Field | Value |
   |-------|-------|
   | PyPI Project Name | `monolith-ai` |
   | Owner | `keyurpatel446` |
   | Repository name | `Monolith` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

That's it — no secrets. The next tag triggers a build and upload.

## Cutting a release

1. Bump `version` in `pyproject.toml` and update `CHANGELOG.md`.
2. Merge `develop → master`. CI tags `vX.Y.Z`, creates a GitHub release, and the
   publish workflow uploads to PyPI.

## Test runs (optional)

To validate the pipeline without touching real PyPI, add a second Trusted
Publisher on **TestPyPI** and a workflow step with
`repository-url: https://test.pypi.org/legacy/`. Remove it once you're
confident.

## Falling back to a token

If you prefer token auth, add a `PYPI_API_TOKEN` repo secret and give the
publish step `with: { password: ${{ secrets.PYPI_API_TOKEN }} }`. Trusted
Publishing is recommended because there's no secret to rotate or leak.
