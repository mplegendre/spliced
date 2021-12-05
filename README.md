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

### Install

You can clone and then install the library locally:

```bash
$ git clone https://github.com/buildsi/spliced
$ cd spliced
$ python -m venv env
$ source env/bin/activate
$ pip install -e .
```

or for releases:

```bash
$ pip install spliced
```

### Config File

A spliced config file is going to help you generate splicing commands, either to run yourself locally or to hand
of to an automated solution. It's a simple YAML file that should have the following:

```yaml
package: curl
splice: zlib
command: curl --head https://linuxize.com/
```

It's currently a flat list because we have one of each, and this can be adjusted as needed.
Each of these is considered one experiment. You should not include versions with the package
to be spliced, or the library to splice in, as they will be discovered programatically.
The above says:

> Take the binary 'curl' for the package curl, and replace the chosen version of zlib with all other versions of zlib.

You can also ask to splice in a totally different dependency:

```yaml
package: hdf5
splice: openmpi
replace: mpich
...
```

The above says

> Take the hdf5 package, and replace openmpi with mpich.

When you don't include a "replace" field, the replacement library is implied to be the same as the spliced one.
To then run the workflow, simply input "curl.yaml" as the splice variable in the GitHub
workflow interface. If you don't include a command, then the splice and prediction can still happen,
but we don't have a good way to test if the binary still (minimally) runs.


### Splice Commands

Thus the first thing we might want to do is take a config YAML file, and see all the commands it can generate
for us.

```bash
$ spliced command examples/curl.yaml
spliced splice --package curl@7.74.0 --splice zlib --runner spack --replace zlib --experiment curl curl --head https://linuxize.com/
spliced splice --package curl@7.68.0 --splice zlib --runner spack --replace zlib --experiment curl curl --head https://linuxize.com/
...
spliced splice --package curl@7.72.0 --splice zlib --runner spack --replace zlib --experiment curl curl --head https://linuxize.com/
spliced splice --package curl@7.49.1 --splice zlib --runner spack --replace zlib --experiment curl curl --head https://linuxize.com/
```

It looks exactly as you'd expect - every version of curl with instruction to splice zlib (meaning different versions) and a command (the last part of the line)
to test. Given the expeiment runner is spack, spack will receive this request and handle install, etc. We could then try running one of those commands, discussed
next.

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

By default, the predictors used will be all that are provided (libabigail and symbolator and an actual) and if
any predictor dependency is missing, a warning will be printed and it will be skipped. If you want to filter
to a specific number of predictors, use `--predictor` for each.

```bash
$ spliced splice --package curl@7.50.2 --splice zlib --experiment curl --predictor symbolator
```

Note that the "actual" run is always performed if a command is provided, but not if it isn't.
The above would run the experiment with a symbolator prediction. Here is what an entire run looks like, with a testing command and 
output saved to a json file with `--outfile`

```bash
$ spliced splice --package curl@7.50.2 --splice zlib --runner spack --replace zlib --experiment curl --outfile examples/curl-result.json curl --head https://linuxize.com/
Concretizing curl@7.50.2
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/berkeley-db-18.1.40-pdlzkb4o4qsw3nglppv7eqjm7lepqvod
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/libiconv-1.16-infpf4xwcb7253odbry6ljjcsat2ksp5
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/pkgconf-1.8.0-5bckkoeicca3dtolbeyz6tnnyxwcsfn5
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/diffutils-3.8-ae4ve7adrxntd2kafm4xxmeyhrwpzpmg
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/ncurses-6.2-5bzr63iqgpogufanleaw2fzjxnzziz67
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/bzip2-1.0.8-doeyikigv6jk4dk6fdxm3cl5j7j465if
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/readline-8.1-wkga37hicua476jm2bjjmuzufz6h574j
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/gdbm-1.19-wuhyaf477mw6nmgftp3gvrxic7qzgpso
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/perl-5.34.0-bvgnm2ejnajpvaruta22d5c24g6qi4zu
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/openssl-1.1.1l-antishvjbtniecep64dku2cenh7hkonc
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/curl-7.50.2-a7ncgyeci2upn3vimpc62whvdkagihou
Testing splicing in (and out) zlib@1.2.11
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px
Testing splicing in (and out) zlib@1.2.8
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.8-mtdthhgpvdcqsfmbqzzvdlvain56j6th
Testing splicing in (and out) zlib@1.2.3
[+] /home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.3-mum2pz5di4xf4pjkyac3olgpnbrtpxph
Making predictions for actual
Making predictions for symbolator
```

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

### 1. An Experiment

The core of an experiment is to be able to run the initial steps for a splice,
and return the splice object, which should have binaries and libraries for a spec pre and post splice,
along with other metadata. This general format allows us to have an experiment runner like spack
(that will install what we need and then set the paths) or eventually a manual runner (where we can just
set them arbitrarily to our liking).

### 2. A Predictor

A predictor should be added as a module to [spliced/predict](spliced/predict) so it is retrieved
on init. It should have a main function, predict, which takes a splice object and optional kwargs.
At this point you can iterate through the splice structure to use whatever metadata you need. E.g.,:

 - splice.libs: is a dictionary with "original" and "spliced" for original and spliced libs, respectively
 - splice.binaries: is the same structure, but with binaries for the original and spliced package
 
Importantly, your predictor should set `spliced.predictions[<name_of_predictor>]` to be a list of dictionaries,
where you can put any needed metadata. The binary/lib is suggested, along with a return code or message from the console,
and *importantly* you should have a boolean true/false for "prediction" about whether the splice is predicted to work.
Here is an example list of results (with a single splice prediction using abicompat) from libaibgail.

```
"predictions": {
    "libabigail": [
        {
            "message": "",
            "return_code": 0,
            "binary": "/home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/curl-7.50.2-7ybfviq4uauvq4hhggxn3npc6ib4clr3/bin/curl",
            "lib": "/home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px/lib/libz.so.1.2.11",
            "original_lib": "/home/vanessa/Desktop/Code/spack-vsoch/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px/lib/libz.so.1.2.11",
            "prediction": true
        }
    ],
```

To be clear, the predictor must save a list of predictions to the splice.predicitions, keyed by the name, and the following fields are requried:

 - binary
 - lib
 - prediction
 
The following fields are not required but suggested:

 - message (the terminal output of running the predictor)
 - return_code
 - original_lib or original_binary if relevant for the command
 - any other relevant results information

### 3. Creating a container base

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
 
## TODO

 - need pretty docs with branding
 - GitHub action to generate splice result interface from splice repository with artifacts
 - update spliced-results repo to use it
 - then do release of spliced on pip
 
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
