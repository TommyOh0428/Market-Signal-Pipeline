---
name: msp-deploy
description: Implement, review, or test Market Signal Pipeline Google Cloud and Terraform deployment work. Use for Cloud Scheduler, Pub/Sub, authenticated push subscriptions, Cloud Run, Firestore, Secret Manager, Artifact Registry, Cloud Logging, IAM, environment variables, deployment configuration, and cloud validation.
---

# MSP Cloud Deploy

## GCP Services

The README architecture uses:

- Cloud Scheduler
- Pub/Sub
- Cloud Run
- Firestore
- Secret Manager
- Artifact Registry
- Cloud Logging

## Deployment Rules

- Cloud Scheduler should publish the scheduled market-analysis event to Pub/Sub.
- Pub/Sub should invoke Cloud Run through an authenticated push subscription.
- Cloud Run should receive only the minimum configuration required to run: project IDs, watchlist, provider settings, secret names, and email configuration.
- Store credentials in Secret Manager or environment-managed secrets, not Terraform plaintext or source code.
- Prefer narrow IAM roles over broad project-level grants.

## Terraform Guidance

- Keep resources named predictably around the pipeline purpose and environment.
- Make region, project ID, service name, schedule, watchlist, and notification settings configurable.
- Avoid mixing application business logic into Terraform.
- Output only operationally useful values such as service URL, topic name, scheduler job name, or artifact repository.

## Validation

- For local validation, run formatting and static checks available in the repo.
- For cloud validation, check Scheduler -> Pub/Sub -> Cloud Run invocation flow, Firestore writes, logs, and email delivery.
- Do not run live deploys unless the user explicitly asks and required credentials are present.
