# Security baseline checklist

Documented security baseline for the lightweight CI/CD pipeline. As stated in the
research proposal, security is handled as a documented reference checklist rather
than enforced gates, since building and testing full security controls would
constitute a project in its own right.

## Secrets and credentials
- [ ] No credentials, tokens, or API keys are hard-coded anywhere in the repository.
- [ ] All deployment tokens are stored in GitHub encrypted secrets.
- [ ] The Render deploy hook URL is stored as `RENDER_DEPLOY_HOOK_URL` secret.
- [ ] Secrets are never echoed to workflow logs.

## Container
- [ ] Base image is a minimal image (node:20-alpine).
- [ ] Container runs as a non-root user (`USER node`).
- [ ] Multi-stage build keeps build tooling out of the runtime image.
- [ ] `.dockerignore` excludes node_modules, .git, and docs from the build context.

## Workflow permissions
- [ ] Workflow uses least-privilege `permissions` (contents: read, packages: write).
- [ ] Default `GITHUB_TOKEN` is used for registry auth rather than a personal token.

## Dependencies
- [ ] Dependencies are installed reproducibly (`npm ci` where a lockfile exists).
- [ ] Production image installs production dependencies only (`--omit=dev`).

## Licensing and attribution
- [ ] Project is published under the MIT License.
- [ ] All third-party and open-source code fragments are attributed.
