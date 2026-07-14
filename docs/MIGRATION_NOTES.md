# Migration notes

The Harborlight rebuild replaces a broad personal notebook collection with one focused tutorial.

| Legacy item | Current replacement |
|---|---|
| Root third-party transcript | Removed; Git history retains it |
| Scratch API connection notebook | Removed |
| Four active legacy notebooks | Archived unchanged under archive/legacy_notebooks |
| utils package | src/harborlight_responses package |
| requirements.txt | pyproject.toml with core and optional extras |
| Hand-maintained model catalog | Environment-only two-tier resolver |
| Raw HTTP first lesson | Current OpenAI Python SDK |
| Manual prose JSON parsing | Pydantic and responses.parse |
| Incomplete local tool execution | Full function_call_output continuation loop |
| Stale live web output | Dated fixture or explicitly dated live hosted search |
| No application | Focused two-workflow Renewal Desk |
| No CI | Ruff, pytest, five keyless notebooks, and app import on Python 3.10/3.13 |

Historical review documents remain in docs/history. docs/FABLE_RECOMMENDATIONS.md is preserved byte-for-byte from the local report supplied for this rebuild.