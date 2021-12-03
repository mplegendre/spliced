# Spliced

<img src="https://github.com/buildsi/spliced/raw/main/docs/img/spliced.png" width="300px">

🚧️ under development 🚧️

[![GitHub actions status](https://github.com/buildsi/spliced/workflows/spliced/badge.svg?branch=main)](https://github.com/buildsi/spliced/actions?query=branch%3Amain+workflow%3Aspliced)

Spliced is software for performing or emulating splices, meaning subbing in one version of a library
for another, and predicting (through many avenues) whether it will work or not. A few concepts of
interest:

 - A **package** is a primarily library that we want to cut (or splice) up.
 - A **spliced out** library is a dependency or linked library that we are removing.
 - A **spliced in** library is a dependency or linked library that we want to sub in.
 
Note that [spack](https://github.com/spack/spack) is required to be on your path
given that you are running a spack matrix build, otherwise don't worry. If spack
is not found you will be issued an instruction to install it.

```bash
$ git clone --depth 1 https://github.com/spack/spack
$ source spack/share/spack/setup-env.sh
```
 
## Usage

### Splice

The most basic functionality is to perform a splice! You can either [generate a matrix](#splice-matrix) via a config file, 
provide the same config file to splice (appropriate for runners with custom variables to include like library paths)
or come up with your own.  Current runners supported include:

 - spack
 
And likely we will add a "manual" runner soon. 

#### Spack Splice

Let's start with an example command that says:

> splice all versions of zlib to replace the current version of zlib in curl

```bash
$ spliced splice --package curl@7.50.2 --splice zlib --runner spack --replace zlib --experiment curl
```

Since we only have one runner (spack) that's currently the default, so this works too:

```bash
$ spliced splice --package curl@7.50.2 --splice zlib --replace zlib --experiment curl
```

Also if you are splicing the same library in (e.g., different versions) you can leave out replace:

```bash
$ spliced splice --package curl@7.50.2 --splice zlib --experiment curl
```

The experiment is just a named identifier, for your use (to store with the results). When you do this
you'll see:

1. Concretizing curl@7.50.2: the main package concretizing and installing. If either of these steps fails, you'll get a result object reporting the error.
2. Splicing (for each version of the dependency found) this can also have various points of failure, which are logged.
3. Running splice predictors (not developed yet) but will give a prediction if the splice will work!
4. Commands, if provided, are then run to give an "actual" report of if it worked (according to the command) or not.


### Splice Matrix

While you can perform a single splice manually, generally you'd want to instead create a matrix!
You can do this with the `splice matrix` command, which will output json that you can use in GitHub or other CI workflows.
The spliced format

```bash
$ spliced matrix examples/curl.yaml 
```

If you provide a custom container base, it will be included in the matrix and compilers discovered from it:
```bash
$ spliced matrix examples/curl.yaml --container ghcr.io/buildsi/spack-ubuntu-20.04
```

This will output a matrix of commands and other metadata that you can use in GitHub actions or your CI tool of choice. 

```bash
$ spliced matrix examples/sqlite.yaml 
::set-output name=containers::[{"command": "spliced splice --package sqlite@3.27.0 --splice zlib --replace zlib --experiment sqlite", "package": "sqlite@3.27.0", "splice": "zlib", "replace": "zlib", "experiment": "sqlite", "container": null}, {"command": "spliced splice --package sqlite@3.28.0 --splice zlib --replace zlib --experiment sqlite", "package": "sqlite@3.28.0", "splice": "zlib", "replace": "zlib", "experiment": "sqlite", "container": null}, {"command": "spliced splice --package sqlite@3.29.0 --splice zlib --replace zlib --experiment sqlite", "package": "sqlite@3.29.0", 
...
"splice": "zlib", "replace": "zlib", "experiment": "sqlite", "container": null}, {"command": "spliced splice --package sqlite@3.30.0 --splice zlib --replace zlib --experiment sqlite", "package": "sqlite@3.30.0", "splice": "zlib", "replace": "zlib", "experiment": "sqlite", "container": null}, {"command": "spliced splice --package sqlite@3.27.2 --splice zlib --replace zlib --experiment sqlite", "package": "sqlite@3.27.2", "splice": "zlib", "replace": "zlib", "experiment": "sqlite", "container": null}, {"command": "spliced splice --package sqlite@3.35.5 --splice zlib --replace zlib --experiment sqlite", "package": "sqlite@3.35.5", "splice": "zlib", "replace": "zlib", "experiment": "sqlite", "container": null}]
```

If you want to limit the number of results (if versions exceed this it will randomly sample to the limit):

```bash
# 256 is the job limit for GitHub actions
$ spliced matrix examples/curl.yaml --limit 256

# An example to show much fewier
$ spliced matrix examples/curl.yaml --limit 3
Warning: original output is length 29 and limit is set to 3 jobs!
::set-output name=containers::[{"command": "spliced splice --package curl@7.71.0 --splice zlib --replace zlib --experiment curl", "package": "curl@7.71.0", "splice": "zlib", "replace": "zlib", "experiment": "curl", "container": null}, {"command": "spliced splice --package curl@7.49.1 --splice zlib --replace zlib --experiment curl", "package": "curl@7.49.1", "splice": "zlib", "replace": "zlib", "experiment": "curl", "container": null}, {"command": "spliced splice --package curl@7.59.0 --splice zlib --replace zlib --experiment curl", "package": "curl@7.59.0", "splice": "zlib", "replace": "zlib", "experiment": "curl", "container": null}]
```

Finally, you can save the result directly to output file (json) instead:

```bash
$ spliced matrix examples/curl.yaml --outfile examples/curl-matrix.json
```


## Development

### 1. Creating a container base

Typically, a container base should have the dependencies that you need to run your
splice. E.g., if you want to use the libabigial splicer, libabigail should
be installed. We provide a set of automated builds for containers to provide the software 
needed [here](docker) (e.g., including libabigail, spack, and symbolator) so you can use this container set,
or if you choose, bootstrap these containers for your own customization. Note that for these containers:

 - we provide several os bases - the default of the spliced execuable is ubuntu 20.04, and you can change this with `--container`
 - the containers are flagged with [spack labels](https://github.com/spack/label-schema) for `org.spack.compilers` to be discovered by the tool. If you don't provide labels, all compilers in the container will be used.
 - it's assumed you have software you need in the container, or use our container bases as testing CI bases and install there on the fly.
 
If you want to use the default containers provided by spliced, you shouldn't need to worry about this.
If you have any questions, don't hesitate to open an issue.
 
## License

Spack is distributed under the terms of both the MIT license and the
Apache License (Version 2.0). Users may choose either license, at their
option.

All new contributions must be made under both the MIT and Apache-2.0
licenses.

See [LICENSE-MIT](https://github.com/spack/spack/blob/develop/LICENSE-MIT),
[LICENSE-APACHE](https://github.com/spack/spack/blob/develop/LICENSE-APACHE),
[COPYRIGHT](https://github.com/spack/spack/blob/develop/COPYRIGHT), and
[NOTICE](https://github.com/spack/spack/blob/develop/NOTICE) for details.

SPDX-License-Identifier: (Apache-2.0 OR MIT)

LLNL-CODE-811652
