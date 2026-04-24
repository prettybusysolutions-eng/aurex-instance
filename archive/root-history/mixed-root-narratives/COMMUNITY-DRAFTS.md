# Community Drafts

Last updated: 2026-04-13 18:29 EDT
Status: READY

## Draft 1 - Session drift / continuity thread
I kept running into session drift and messy resume handoffs, so I wrote a small utility to sanity-check the local runtime surfaces before I start fixing anything. It just generates a local report and stays non-destructive. If that problem sounds familiar, this may help: Runtime Doctor.

## Draft 2 - Workspace chaos / residue thread
I had a recurring problem where it became hard to tell what in the workspace was canonical versus runtime residue versus just stuff that needed review. I wrote a simple residue classifier script for that. It does not delete anything, it just writes a report so cleanup decisions are safer.

## Draft 3 - Config breakage / debugging thread
A lot of debugging time was getting wasted on vague config drift and hidden state issues, so I broke out two internal utility scripts I was already using: one for runtime diagnosis and one for residue classification. They are both local, non-destructive, and meant to reduce guesswork.
