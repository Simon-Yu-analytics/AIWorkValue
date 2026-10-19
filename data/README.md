# Data provenance and local-data policy

The study is Noy and Zhang (2023), [Science, DOI 10.1126/science.adh2586](https://doi.org/10.1126/science.adh2586). The authors host their replication materials at [OSF xd7qw](https://osf.io/xd7qw/).

`source-manifest.json` records nine source assets, download URLs, byte counts and SHA-256 hashes. From the repository root, `make download` retrieves and verifies them. `make run` reconstructs the sample and creates the local analysis files.

| Location | Contents | Distributed? |
|---|---|---|
| `source-manifest.json` | Public source references and file hashes | Yes |
| `scenarios/weekly_status_email.json` | Hypothetical task-frequency/checking assumptions | Yes; no participant data |
| `raw/` | Author survey, grading files and replication documentation | No; Git-ignored |
| `processed/participants.csv` | Participant-level analysis variables | No; Git-ignored |
| `processed/study.sqlite` | Participant-level SQLite table | No; Git-ignored |
| `../reports/` | Aggregate audit, effects and SQL tables | Yes |

The source OSF node declared no license in its metadata when inspected. Public availability is not treated as permission to redistribute the raw research materials. The loader reads selected analytical columns; no participant essays are displayed in the public notebook or reports.

See the [data and methods protocol](../docs/DATA_AND_METHODS.md) for sample construction, variable definitions and limitations, and [third-party notices](../THIRD_PARTY_NOTICES.md) for attribution.
