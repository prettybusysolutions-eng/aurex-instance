# Usage Example

Copy-pasteable GitHub Actions workflow:

```yaml
name: runtime-doctor

on:
  workflow_dispatch:
  push:

jobs:
  diagnose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Runtime Doctor
        uses: prettybusysolutions-eng/runtime-doctor@main
        with:
          workspace-path: .
          output-path: runtime-doctor-report.json
      - name: Show report
        run: cat runtime-doctor-report.json
```
