<!-- SPDX-License-Identifier: 0BSD -->

# Installation - Dev Containers (EXPERIMENTAL!)

palgoviz has [a dev container configuration](../.devcontainer/), but it is
experimental.

A [dev container](https://code.visualstudio.com/docs/devcontainers/containers)
created from this configuration has palgoviz installed in it in *both* the
supported ways: [with conda/mamba](install-with-conda.md) and [with
poetry](install-with-poetry.md). You can use either one or switch between them
(just as you could if you followed both installation methods outside a dev
container).

You can use the dev container in the cloud [with GitHub
Codespaces](https://github.com/features/codespaces), or locally [with VS Code
and Docker](https://code.visualstudio.com/docs/devcontainers/containers).

## Limitations

There are two major limitations: container creation is very slow, and the
container doesn’t run JupyterLab reliably enough.

### Container creation is very slow

We don’t have our own Docker image. Instead, the palgoviz dev container
configuration:

- Uses the `mcr.microsoft.com/devcontainers/python` image (which is the same
  image the dev containers [Python sample
  project](https://github.com/microsoft/vscode-remote-try-python) uses).
- Adds a number of
  [features](https://code.visualstudio.com/blogs/2022/09/15/dev-container-features),
  to provide development tools not present in that Python image, each of which
  is applied when a container is created.
- Adds even more tools in a post-creation action, which also runs when the
  container is created.
- Installs palgoviz with both conda/mamba and poetry in the container, also in
  the post-creation action. This involves downloading and installing all its
  dependencies, both with conda/mamba and, separately, with poetry.

Dev containers are supposed to be lightweight and readily disposable (once you
have pushed your code to a remote, of course). A developer often creates a dev
container for a single use—such as to test a particular change, or do a single
session of work—and then deletes it afterwards. This is especially common when
hosting a dev container [in a
codespace](https://github.com/community/community/discussions/39697). To
support this workflow, dev containers should be quick to (re)create. But the
above steps in container creation, taken together, make the palgoviz dev
container slow to create.

It would be good to have custom Docker images wherein this work has already
been done. At least right now, we have not made any. To be useful, they would
have to be built regularly, so tools and dependencies stay up to date.

### It doesn’t run JupyterLab reliably enough

If you want [to use JupyterLab](../README.md#using-the-notebooks) in the dev
container, you can. But there is at least one major problem.

[In GitHub Codespaces](#running-in-a-codespace), attempting to save changes to
a notebook sometimes takes a long time, occasionally remaining unsaved with no
signs of anything happening for multiple minutes, then failing with [a 504
error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504). It does
not falsely appear to be saved. But this can nonetheless be a big barrier to
usability. It seems that saving always eventually succeeds, if attempted enough
times, but sometimes it takes several tries, spanning a significant time.

While there has been some testing of JupyterLab from a [locally run palgoviz
dev container](#running-locally-with-vs-code-and-docker), and it usually seems
to work okay, this has not been tested extensively enough to gauge reliability.

In contrast, VS Code seems to work at least as well in the dev container as it
normally does, including for notebooks. However, you may still prefer
JupyterLab, at least some of the time. This is because, whether or not you are
using a dev container, VS Code is [not currently
heeding](using-notebooks.md#notebooks-in-vs-code) the `raises-exception` cell
tag (at least as it occurs in this project’s notebooks).

## Running in a codespace

You must have GitHub account, and log in, to use [GitHub
Codespaces](https://github.com/features/codespaces).

See [this further
documentation](https://code.visualstudio.com/docs/remote/codespaces) for more
information on GitHub Codespaces.

*Note that GitHub Codespaces is a cloud-based service with [monthly usage
limits](https://github.blog/changelog/2022-11-09-codespaces-for-free-and-pro-accounts/).
(You can set up billing if you need more.)*

### What repository is cloned in the codespace

Although you need not
[fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the
palgoviz repository on GitHub to create a codespace, you might want to.

Whether or not you fork, the codespace you create is private. One benefit of
forking the project is that it makes it easier to keep track of what commit you
created your codespace from, because while GitHub makes it easy to synchronize
your fork with the upstream repository, it doesn’t automatically do that.
Another is that you can easily commit your changes to your fork.

#### Without forking

1. Go to [palgoviz on GitHub](https://github.com/EliahKagan/palgoviz).
2. Click the green “Code” button.
3. The menu that comes up has a “Local” tab and a “Codespaces” tab. Click the
   “Codespaces” tab.
4. Click “Create codespace on main.”

#### With forking

[Fork the
project.](https://docs.github.com/en/get-started/quickstart/fork-a-repo) Then
do [the above](#without-forking), but in your fork instead of in the upstream
project.

You can create the codespace for any branch. That branch will be checked out
into the codespace initially, but the dev container in the codespace will have
access to other branches. For example, if you create the codespace for your
main branch, you’ll still be able to switch (or even create) a feature branch
and use it to work on the feature branch.

### Client Applications

#### Web interface

The above instructions describe using the web-based interface. That uses a
version of VS Code in your web browser. It is separate from, and does not
require, the VS Code application on your computer.

As of this writing, this works better with Chromium-based browsers, such as
Google Chrome, than with Firefox. (If you do use Firefox, the experience can
[sometimes be
improved](https://github.com/github/codespaces-getting-started-ml#warning) by
[turning off enhanced tracking
protection](https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop#w_what-to-do-if-a-site-seems-broken)
after after entering the codespace. Every codespace has its own separate
domain.) You can switch between browsers without having to restart the
codespace.

#### Visual Studio Code

If you like, you can use a codespace from the installation of VS Code on your
computer instead, using the [Codespaces
extension](https://marketplace.visualstudio.com/items?itemName=GitHub.codespaces).
This works on all platforms that support VS Code. **This should *not* be
confused with [running the container](#running-locally-with-vs-code-and-docker)
locally.** In this situation, you are using the installed version of VS Code,
which is not in your web browser. But the dev container you are interacting
with is still running in a codespace, on the cloud—*not* on your computer.

#### The progressive web app

There is also [the Codespaces
application](https://code.visualstudio.com/docs/remote/codespaces#_known-limitations-and-adaptations).
This is a [progressive web
app](https://learn.microsoft.com/en-us/microsoft-edge/progressive-web-apps-chromium/).

## Running locally with VS Code and Docker

You can [create a dev container locally with VS Code and
Docker](https://code.visualstudio.com/docs/devcontainers/containers).

### Installing prerequisites

You need:

- [Docker](https://www.docker.com/).
- The [Dev Containers
  extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  for VS Code.

You can [**follow these
steps**](https://code.visualstudio.com/docs/devcontainers/containers#_installation)
to install them.

### On Windows, limiting memory usage *(optional)*

If you are running Docker on Windows, you are probably using the [WSL 2
backend](https://docs.docker.com/desktop/windows/wsl/). In that case, you might
want to limit the total amount of memory that all WSL 2 systems, taken
together, are allowed to allocate. (This is useful because it can otherwise
grow quite high, and take a bit of time to be released for use by the rest of
the system.) If you want to do that, you can create a
[`.wslconfig`](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#configuration-setting-for-wslconfig)
file in your [home directory](https://en.wikipedia.org/wiki/Home_directory).
For example, this limits to 2 gigabytes:

```text
[wsl2]
memory=2GB
```

2 gigs is sufficient for a palgoviz dev container.

### Ways to create the container

However you create or container, Docker needs to be running.

#### Suggestion: Clone Repository in Container Volume

The best to work with palgoviz in a locally hosted dev container is usually to
use the [Dev Containers: Clone Repository in Container
Volume...](https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-a-git-repository-or-github-pr-in-an-isolated-container-volume)
action. To do this, you don’t need to have cloned anything beforehand, and if
you have, you don’t need to (and shouldn’t) open the local folder first.

If you [forked](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
palgoviz, then it should appear as an option. If not, and you want to clone the
upstream palgoviz repository rather than making a fork, then you can type or
paste in `EliahKagan/palgoviz` (or paste in [the
URL](https://github.com/EliahKagan/palgoviz)).

#### Alternative approaches

If you have cloned the repository and you open it in VS Code, you should see a
notification from the Dev Containers extension. (If you don’t, [see
below](#alternative-approaches-if-you-dont-see-the-notification).)

On a GNU/Linux system such as Debian or Ubuntu (including a system in WSL 2 or a virtual machine that you are connected to in VS Code), the notification says:

> Folder contains a Dev Container configuration file. Reopen folder to develop
> in a container ([learn
> more](https://code.visualstudio.com/docs/devcontainers/containers)).

Otherwise, you are running Windows or macOS (the Dev Containers extension only
supports these three families of operating systems) and the notification says:

> Folder contains a Dev Container configuration file. Reopen folder to develop
> in a container ([learn
> more](https://code.visualstudio.com/docs/devcontainers/containers)). Or:
> Clone repository in Docker volume for [better I/O
> performance](https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-a-git-repository-or-github-pr-in-an-isolated-container-volume).

One of the main benefits of a dev container is isolation, but if you *want* to
work on the copy of the files in the repository you cloned to disk (rather than
cloning separately in the container), you can do that by clicking “Reopen in
Container.” If you are not on GNU/Linux when you do this, however, then it will
be slow—even slower [than usual](#container-creation-is-very-slow) to create
the dev container, and then slow to use it as well.

In contrast to the “Reopen in Container” button, the “Clone in Volume” button
(shown on Windows and macOS) works the same as [Clone Repository in Container
Volume](#suggestion-clone-repository-in-container-volume), but it gets the
information about where to find the repository (and what branch to use) from
the currently cloned repository and its configured remotes. Note that [Clone
Repository in Container
Volume](#suggestion-clone-repository-in-container-volume) is in no way limited
to Windows and macOS, and you should perhaps be using that anyway, no matter
what operating system you are running. Rather, it is only suggested in Windows
and macOS systems because the alternative of proceeding to access the
already-cloned files from inside a Docker container is much slower on those
systems.

#### Alternative approaches: if you don’t see the notification

If the notification doesn’t come up, the cause is usually one of:

- The Dev Containers extension is not installed (or not enabled).
- Docker is not running. The daemon/service must be running. If you are using
  Docker Desktop, you can run that, and it should start any necessary services.
  You can also use it to check their status.
- You dismissed the notification before, by clicking “Don't Show Again...”
  (Dismissing it by clicking the “X” does not suppress it.)

If you set the notification not to be shown and want to undo that, you then
open the command pallette (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>, or
<kbd>F1</kbd>) and search for “Dev Containers: Reset Don't Show Reopen
Notification.”

## Updating a dev container

One common use of dev containers it to use for a short time—a fraction of a
day. Then updating is rarely useful.

If you use it longer, you may want to update the palgoviz’s dependencies. This
is no different in a dev container than usual: follow the update procedures
[for conda/mamba](install-with-conda.md#updating-the-environment) and [for
poetry](install-with-poetry.md#updating-dependencies) (or maybe just one, if
you’re only using one in the dev container). This is taken care of when the dev
container is created, so you might consider creating a new dev container
instead.

Updating other tools and the system components inside the dev container is
occasionally possible but not suggested. It is better to create a new dev
container instead.
