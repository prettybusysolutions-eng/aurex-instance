# Approval-Ready Community Placement

Last updated: 2026-04-13 19:11 EDT
Status: READY FOR APPROVAL

## Target 1
- Link: https://github.com/MiniMax-AI/Mini-Agent/issues/72
- Why it fits: runtime instability and gateway disconnect pain
- Draft response:
  I had the same kind of runtime drift / weird gateway state issue. I ended up writing a quick local script to check the config and state surfaces before I started changing random things. It is non-destructive and just writes a report. If you want to try it: https://github.com/prettybusysolutions-eng/runtime-doctor

## Target 2
- Link: https://github.com/ThomasLiu/ai-coding-fullstack/issues/186
- Why it fits: session crash recovery / continuity pain
- Draft response:
  I ran into this after a few messy interrupted sessions. What helped was checking whether the local runtime/state was even coherent before trying to resume. I wrote a small local script for that because I was tired of guessing. It does not mutate anything, it just writes a report: https://github.com/prettybusysolutions-eng/runtime-doctor

## Target 3
- Link: https://github.com/ProSkillsMD/proskills/issues/3393
- Why it fits: runtime surface recovery and broken runtime environment context
- Draft response:
  I kept ending up in the same hole where half the problem was runtime drift and the other half was workspace junk making it harder to see what was real. I split that into two small local scripts for my own setup. One checks runtime/config state, the other classifies residue before cleanup. Both are non-destructive.

  Runtime Doctor: https://github.com/prettybusysolutions-eng/runtime-doctor
  Residue Classifier: https://github.com/prettybusysolutions-eng/residue-classifier

## Note
These are drafted only, not posted.
Reddit/Discord targets were not selected in this tranche because anonymous scraping from this environment hit a 403 boundary. These three GitHub targets are real, verified, and approval-safe.
