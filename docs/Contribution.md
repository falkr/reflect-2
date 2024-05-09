# Commit Conventions and Branch Structure

This document outlines the conventions for committing code and the structure of branches within our repository.

## Commit Conventions

### Structure

Commits should follow these example formats:

- feat(front): Lorem ipsum (#1234)
- fix(back): Lorem ipsum (#1234)
- doc: Lorem ipsum (#1234)
- ref(full): Lorem ipsum

#### Rules

- **Type**: Indicates the purpose of the commit. Valid types include:
  - `feat` - A new feature
  - `fix` - A bug fix
  - `doc` - Documentation only changes
  - `ref` - Refactoring code
  - `revert` - Reverting a previous commit
  - `style` - Formatting, missing semi colons, etc; no code change

- **Scope**: Specifies the part of the codebase affected by the commit:
  - `front` - Frontend
  - `back` - Backend
  - `db` - Database
  - `full` - Fullstack

- **Description**: A brief description of the changes.

- **Issue Number**: The associated issue number. This part is only included in the merge commit when the branch is merged with the `dev` branch.

### Body

If the commit header is not self-explanatory, a more detailed body description should be included.

### Co-authors

Use the following syntax to credit co-authors, which is automatic unless the code pairing is done locally:

Co-authored-by: @name

## Branch Structure

### Production branch: `main`

This is the production branch. All commits to `main` must come from the `dev` branch. This branch is protected, and commits can only be made via merge requests from `dev`.

### Development branch: `dev`

The `dev` branch is a protected branch that allows only merge requests and force pushes. Force pushes are permitted in cases of bugs or downtime. The purpose of merge requests is to incorporate changes from the issue branches.

### Issue Branches

These branches are numerous, with each branch corresponding to a specific issue. Each issue branch is merged into `dev` upon completion.

## Guidelines

- Ensure that all commits are clear and descriptive.
- Follow the commit format strictly to maintain consistency across the codebase.
- Merge frequently from issue branches to `dev` to avoid conflicts and integrate changes smoothly.