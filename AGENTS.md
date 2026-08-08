# Repository Instructions

## Git workflow

- After making any set of changes to the skills, always commit the changes directly on the `main` branch and push `main` to the repository.

## Patch workflow

- In this environment, the direct patch helper may fail because its sandbox cannot create an unprivileged user namespace. Apply patches through an elevated `exec_command` invocation instead.
- When passing a patch through a nested shell, protect `$` variables, backticks, and quotes from shell interpolation. Base64-encode the patch and pipe it through `base64 -d | apply_patch` when necessary.
