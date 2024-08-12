# Contributing to PAIG

First off, thanks for taking the time to contribute! The following is a set of guidelines for contributing to PAIG.
These are just guidelines, not rules, so use your best judgment and feel free to propose changes to this document in a
pull request.

## Contents
- [Version Control, Git, and GitHub](#version-control)
- [Getting Started with Git](#getting-started)
- [Submitting a Pull Request](#submitting-a-pull-request)

## Version Control, Git, and GitHub<a name="version-control"></a>

PAIG is hosted on [GitHub](https://github.com), and to contribute, you will need to sign up for
a [free GitHub account](https://github.com/signup). We use Git for version control to allow many people to work together
on the project.

If you are new to Git, you can reference some of these resources for learning Git:

- [Git Documentation](https://git-scm.com/doc)

The project follows a forking workflow whereby contributors fork the repository, make changes, and then create a pull
request. Please read and follow all the instructions in this guide.

## Getting Started with Git<a name="getting-started"></a>

[GitHub has instructions](https://docs.github.com/en/get-started/getting-started-with-git/set-up-git) for installing Git, setting up your SSH key, and configuring Git. Complete these steps before you work seamlessly between your local repository and GitHub.

## Submitting a Pull Request<a name="submitting-a-pull-request"></a>

Pull Requests (PRs) are the way concrete changes are made to the code, documentation, dependencies, and tools contained
in the PAIG repository. Commit messages should be clear, explaining the committed changes.
Update [CHANGELOG.md](CHANGELOG.md) with the changes you made:

Under the "Unreleased" section, use the category most suitable for your change (changed/removed/deprecated). Document
the change with simple, readable text and push it as part of the commit. In the next release, the change will be
documented under the new version.

Before sending your pull requests, make sure you do the following:
- [Read the Code of Conduct](CODE_OF_CONDUCT.md)

### 1. Create a fork of PAIG
  You will need your own copy of paig to work on the code. Go to the paig project page and hit the Fork button. 
  <br>You will want to clone your fork to your machine
  
  ```bash
  git clone git@github.com:<username>/paig.git
  cd paig
  git remote add upstream git@github.com:privacera/paig.git
  git fetch upstream
  ```

### 1. Create a Fork of PAIG

You will need your own copy of PAIG to work on the code. Go to the PAIG project page and hit the Fork button. Clone your
fork to your machine:

```bash
git clone git@github.com:<username>/paig.git
cd paig
git remote add upstream git@github.com:privacera/paig.git
git fetch upstream
```

### 2. Creating a Feature Branch

Your local main branch should always reflect the current state of the PAIG repository. First, ensure it’s up-to-date
with the main PAIG repository:

```bash
git checkout main
git pull upstream main --ff-only
```
Then, create a feature branch for making your changes:
```bash
git checkout -b feature-branch-name
```

Keep changes in this branch specific to one bug or feature. You can have many feature branches and switch between them
using the `git checkout` command.

### 3. Making Code Changes<a name="code-changes"></a>

Before modifying any code, set up an appropriate development
environment [Setup Development Environment](../backend/paig/README.md). After making code changes, see all the changes
you’ve currently made by running:

```bash
git status
```

For files you intended to modify or add, run:

```bash
git add path/to/file-to-be-added-or-changed.py
```

Finally, commit your changes to your local repository with an explanatory commit message:

```bash
git commit -m "your commit message goes here"
```

### 4. Add Test Coverage

Bug fixes and features should always come with tests. A testing guide has been provided to make the process easier.
Before submitting your changes in a pull request, always run the full test
suite: [Testing Guide](../backend/paig/tests/README.md).

### 5. Pushing Your Changes

When you want your changes to appear publicly on your GitHub page, push your forked feature branch’s commits:

```bash
git push origin feature-branch-name
```

Here, `origin` is the default name given to your remote repository on GitHub.

### 6. Making a Pull Request

Once you have finished your code changes, you are ready to make a pull request (PR). Follow these steps:

1. Navigate to your repository on GitHub.
2. Click on the `Compare & pull request` button.
3. Review Changes: Click on the `Commits` and `Files Changed` tabs to ensure everything looks okay one last time.
4. Write a Descriptive Title: Include appropriate prefixes in the title. Common prefixes used by PAIG:
    - **ENH:** Enhancement, new functionality
    - **BUG:** Bug fix
    - **DOC:** Additions/updates to documentation
    - **TST:** Additions/updates to tests
    - **BLD:** Updates to the build process/scripts
    - **PERF:** Performance improvement
    - **TYP:** Type annotations
    - **CLN:** Code cleanup
5. Write a Description: Provide a detailed description of your changes in the `Preview Discussion` tab.
6. Send the Pull Request: Click the `Send Pull Request` button.

### 7. Updating Your Pull Request

Based on the review you get on your pull request, you may need to make changes to the code. Follow **Step 3: Making Code
Changes** to address any feedback and update your pull request.

To update your feature branch with changes in the PAIG main branch:
```bash
git checkout feature-branch-name
git fetch upstream
git merge upstream/main
```

If there are no conflicts, save and quit the commit message file. If there are merge conflicts, resolve them as
explained [here](https://help.github.com/articles/resolving-a-merge-conflict-using-the-command-line/). Once resolved,
run:

```bash
git add -u
git commit
```

If you have uncommitted changes when updating the branch with **main**, stash them prior to updating (see
the [stash docs](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning)).

After updating your feature branch locally, update your pull request by pushing to the branch on GitHub:

```bash
git push origin feature-branch-name
```

Any `git push` will automatically update your pull request with your branch’s changes and restart the Continuous
Integration checks.
