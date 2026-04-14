# OpenClaw Troubleshooting Guide

Last updated: 2026-04-13 22:02 EDT
Status: DRAFT

## Title
OpenClaw Troubleshooting Guide: 5 Common Failures and How to Fix Them

## Meta description
Diagnose OpenClaw runtime drift, gateway disconnects, session recovery failures, and messy workspace cleanup with practical non-destructive troubleshooting steps.

## H1
OpenClaw Troubleshooting Guide

## Intro
If OpenClaw feels unstable, the problem usually is not "everything is broken." It is usually a smaller failure class: runtime drift, bad state, session recovery mismatch, or workspace residue making diagnosis harder than it should be.

This guide covers the most common failures and gives you a clean first-pass troubleshooting path before you start changing random files.

## Section 1 — Gateway disconnects and runtime drift
Symptoms:
- gateway disconnects
- tools behave inconsistently
- the runtime feels different from one session to the next

What to do:
- verify config surfaces first
- check continuity state
- avoid blind edits until the state is mapped

Tool:
- Runtime Doctor
- Pro CTA: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06

## Section 2 — Session recovery keeps failing
Symptoms:
- interrupted sessions do not resume cleanly
- old state conflicts with new expectations
- you are guessing instead of verifying

What to do:
- confirm the runtime/state surfaces are coherent
- isolate residue from live state
- use diagnosis before repair

Tool:
- Runtime Doctor
- Pro CTA: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06

## Section 3 — Workspace cleanup feels dangerous
Symptoms:
- you do not know what is canonical
- root is polluted with runtime exhaust
- deleting things feels risky

What to do:
- classify first
- avoid deletion-first cleanup
- separate canonical, runtime, local-only, and review-needed surfaces

Tool:
- Residue Classifier
- Pro CTA: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07

## Section 4 — Root repo keeps getting messy again
Symptoms:
- the root keeps accumulating generated files
- cleanup does not stick
- you keep revisiting the same residue problem

What to do:
- define root policy
- identify repeat residue classes
- turn cleanup into governance

Tool:
- Residue Classifier
- Pro CTA: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07

## Section 5 — You are losing hours to debugging
Symptoms:
- too much manual checking
- too many unclear failure boundaries
- progress stalls because diagnosis is fuzzy

What to do:
- use the free tools first
- if the issue is deeper, use the Pro path built to save 5+ hours of debugging and cleanup work

## Tool links
- Runtime Doctor: https://github.com/prettybusysolutions-eng/runtime-doctor
- Residue Classifier: https://github.com/prettybusysolutions-eng/residue-classifier
- Runtime Doctor Pro: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06
- Residue Classifier Pro: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07
