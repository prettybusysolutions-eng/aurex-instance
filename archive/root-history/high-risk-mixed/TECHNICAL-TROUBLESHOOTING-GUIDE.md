# OpenClaw Technical Troubleshooting Guide

Last updated: 2026-04-13 21:12 EDT
Status: READY

## 1. OpenClaw runtime feels broken or inconsistent
Common signs:
- gateway disconnects
- tools behave differently across runs
- state feels stale or contradictory

What to check:
- local config integrity
- continuity state presence
- recent runtime drift

Free tool:
- Runtime Doctor

Pro CTA:
- Upgrade to Runtime Doctor Pro: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06

## 2. Session resume keeps going wrong
Common signs:
- interrupted runs are hard to recover
- state does not match expectations
- you waste time guessing before resuming

What to check:
- whether runtime/state surfaces are coherent before resuming
- whether old residue is obscuring live state

Free tool:
- Runtime Doctor

Pro CTA:
- Upgrade to Runtime Doctor Pro: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06

## 3. Workspace cleanup feels risky
Common signs:
- you are not sure what is canonical
- runtime residue pollutes the root
- cleanup feels dangerous because you might delete something real

Free tool:
- Residue Classifier

Pro CTA:
- Upgrade to Residue Classifier Pro: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07

## 4. Root repo is getting messy
Common signs:
- too many generated files in the root
- unclear promote/ignore/archive decisions
- governance drift over time

Free tool:
- Residue Classifier

Pro CTA:
- Upgrade to Residue Classifier Pro: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07

## 5. Debugging is eating hours
Common signs:
- repeated manual checks
- unclear failure boundaries
- cleanup and diagnosis consume more time than actual progress

Recommendation:
Start with the free tools.
If they save you one headache but you still need the deeper path, the Pro versions are priced to save 5+ hours of debugging and cleanup.

## Tool links
- Runtime Doctor: https://github.com/prettybusysolutions-eng/runtime-doctor
- Residue Classifier: https://github.com/prettybusysolutions-eng/residue-classifier
