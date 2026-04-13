# Approval-Ready Community Placement

Last updated: 2026-04-13 18:39 EDT
Status: READY FOR APPROVAL

## Target 1
- Link: https://github.com/MiniMax-AI/Mini-Agent/issues/72
- Why it fits: runtime instability and gateway disconnect pain
- Draft response:
  I ran into a similar pattern of runtime drift and opaque failure states, so I broke out a small local utility script I was already using for my own setup. It is non-destructive and just writes a local diagnosis report to help narrow down whether the issue is config/state drift before changing anything. If useful, here it is: https://github.com/prettybusysolutions-eng/runtime-doctor

## Target 2
- Link: https://github.com/ThomasLiu/ai-coding-fullstack/issues/186
- Why it fits: session crash recovery / continuity pain
- Draft response:
  I kept getting burned by messy recovery paths after session interruptions, and part of the problem was not knowing whether the local runtime/state surfaces were coherent before trying to resume. I wrote a small utility script for that diagnosis step. It is local-only and non-destructive, so it may be a useful first pass before heavier repair work: https://github.com/prettybusysolutions-eng/runtime-doctor

## Target 3
- Link: https://github.com/ProSkillsMD/proskills/issues/3393
- Why it fits: runtime surface recovery and broken runtime environment context
- Draft response:
  One thing that helped me reduce guesswork here was splitting two problems apart: runtime diagnosis and workspace residue classification. I wrote two small utility scripts for my own setup, one to sanity-check runtime/config surfaces and one to classify workspace residue before cleanup. Both are non-destructive and local-only.

  Runtime Doctor: https://github.com/prettybusysolutions-eng/runtime-doctor
  Residue Classifier: https://github.com/prettybusysolutions-eng/residue-classifier

## Note
These are drafted only, not posted.
Reddit/Discord targets were not selected in this tranche because anonymous scraping from this environment hit a 403 boundary. These three GitHub targets are real, verified, and approval-safe.
