# Lightweight CI/CD pipeline — proof of concept

A lightweight, open-source CI/CD pipeline for small containerised JavaScript/TypeScript
projects, built with GitHub Actions and Docker, deploying to a single cloud host (Render).

This is the primary artefact for the HCS522 project "Designing a Lightweight CI/CD
Pipeline for Small Software Projects".

## What the pipeline does

On every push to `main`, GitHub Actions runs three jobs:

1. **build-test** — install dependencies, then lint, build (for TypeScript projects)
   and test with the native Node test runner.
2. **containerise-deploy** — build a Docker image, push it to the GitHub Container
   Registry (ghcr.io), then trigger a deployment to Render via a deploy hook.
3. **record-metrics** — always runs, even when an earlier job fails, and writes the
   run's metrics into a CSV artefact.

Because the metrics job runs with `if: always()`, a failed run is recorded too, so the
deployment success rate reflects failures rather than only the runs that reached
deployment.

## The four metrics

The evaluation is built around four metrics (see the dissertation, section 3.4):

- **Deployment success rate** — the primary reliability indicator.
- **Execution time** — pipeline duration, with cold-start runs separated from warm runs.
- **Configuration footprint** — the files and lines a developer must add or change to
  adopt the pipeline. This is a limited proxy for adoption cost, not a direct measure
  of usability.
- **Recovery time** — the time for the pipeline to return to a successful deployment
  after a failure.

## Planned, controlled fault scenarios

Recovery time cannot be observed unless failures occur. A dependable pipeline may run
many times without failing, so the workflow supports planned, controlled fault
scenarios. Run the workflow manually (the "Run workflow" button, `workflow_dispatch`)
and choose a `fault_scenario`:

- `failing_test` — forces the test step to fail.
- `broken_build` — forces the build step to fail.
- `bad_deploy_credential` — uses an invalid deploy hook so deployment fails.
- `none` — a normal run (the default).

Each injected failure is recorded in the metrics artefact under `fault_scenario`, so
recovery runs can be told apart from the natural runs.

## Repository layout

```
.
├── .github/workflows/cicd.yml          # the pipeline (build-test, containerise-deploy, record-metrics)
├── src/server.js                       # baseline app (App 1)
├── test/server.test.js                 # tests
├── Dockerfile                          # multi-stage build
├── package.json
├── eslint.config.js
└── docs/
    ├── security_baseline.md            # security checklist (Objective 1)
    ├── benchmark_dataset_template.csv  # dataset template (Objective 3)
    └── evaluate.py                     # evaluation script (Objective 4)
```

## Setup — step by step

### 1. Create the repository
Push this folder to a new GitHub repository.

### 2. Create a Render service
1. Sign up at render.com (no credit card required for the free tier).
2. New → Web Service → connect your GitHub repository.
3. Render auto-detects the Dockerfile. Set the instance type to Free.
4. Once created, go to Settings → Deploy Hook and copy the hook URL.

### 3. Add the deploy hook as a GitHub secret
In your GitHub repo: Settings → Secrets and variables → Actions → New repository secret.
- Name: `RENDER_DEPLOY_HOOK_URL`
- Value: the deploy hook URL from Render.

### 4. Trigger the pipeline
Push any commit to `main`, or use the "Run workflow" button (`workflow_dispatch`).
Watch the run under the Actions tab.

### 5. Collect metrics
After each run, download the `metrics-<run_id>` artefact from the Actions run page and
append the values to `docs/benchmark_dataset_template.csv`.

### 6. Evaluate
Once the dataset has recorded runs, produce the summary:

```
python3 docs/evaluate.py docs/benchmark_dataset_template.csv
```

## Running the test applications

For Objective 3, run the pipeline at least ten times against three applications:
- the baseline app in this repo,
- two external open-source JavaScript/TypeScript apps (verify each builds in week 2).

For each external app, copy `.github/workflows/cicd.yml`, the `Dockerfile`, and adjust
the `start`/`test` scripts to match that project. Record the files and lines this takes
as the configuration footprint for that application.

## Local development

```
npm install
npm test
npm start      # serves on http://localhost:3000
```

## References and documentation

This proof of concept is built on the following tools. Their official documentation is
the primary reference for how the pipeline is configured and how it can be adapted.

- GitHub Actions — workflow syntax, jobs, permissions and secrets: https://docs.github.com/en/actions
- Docker — Dockerfile reference, multi-stage builds and best practices: https://docs.docker.com
- GitHub Container Registry (ghcr.io) — publishing and consuming images: https://docs.github.com/en/packages
- Render — deploying a service and using deploy hooks: https://render.com/docs

## License

MIT.
