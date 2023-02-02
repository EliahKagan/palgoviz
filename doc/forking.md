<!-- SPDX-License-Identifier: 0BSD -->

# Forking

[**This article on GitHub has more detailed information on forking
repositories.**](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
This page provides some condensed information about forking repositories, but
it is *not* a substitute for that documentation.

## Why to fork

As GitHub briefly explains forks when you [go to fork
palgoviz](https://github.com/EliahKagan/palgoviz/fork) (or any repository):

> A *fork* is a copy of a repository. Forking a repository allows you to freely
> experiment with changes without affecting the original project.

If all you want is a local copy, it is sufficient to clone the repository. But
if you are going to develop your own changes, and if you are going to use
[Git](https://git-scm.com/) for source control, then you should have a [remote
repository](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes) to
synchronize your local changes with (which also provides some protection
against data loss).

Forking a GitHub repository is a convenient way of using GitHub as your remote.
It also allows you to pull changes from the parent repository, if desired, as
well as to propose changes to the parent repository, if you want to do that.
But it is fine to make a fork even if you never intend to do those things.

Note that forks of public GitHub repositories (like palgoviz) are created as
public repositories.

## How to fork

To fork palgoviz on GitHub:

1. [Sign in to GitHub](https://github.com/login), if you are not currently
   signed in.
2. Visit the [palgoviz repository](https://github.com/EliahKagan/palgoviz) on
   GitHub.
3. Click the “Fork” button, which is near the upper-right corner of the page.
4. On the “Create a new fork” page, click the green “Create fork” button.

You can [click this link instead of doing steps 2 and
3](https://github.com/EliahKagan/palgoviz/fork), if you want.

## Cloning your fork

Having forked palgoviz, you can clone your fork like this:

1. Go to your fork. (These instructions work for cloning *any* GitHub
   repository, once you are at the repository page.)
2. Click the green “Code” button.
3. The menu that comes up a “Local” tab and a “Codespaces” tab. The “Local” tab
   is probably already shown, but if not, click it.
4. Copy a URL (SSH or HTTP) and run paste it after `git clone` in a terminal.

For more on those URLs, and other ways to clone, see [About remote
repositories](https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories),
which is the article linked to by the <kbd>?</kbd> in the “Code” menu.

[*Here’s another link to the article on GitHub with more information on
forks.*](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
