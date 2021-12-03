# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


import spliced.experiment
import spliced.utils as utils
import random
import requests
import os
import sys
import json


def main(args, parser, extra, subparser):

    # Generate a base experiment
    experiment = spliced.experiment.Experiment()
    experiment.load(args.config_yaml)

    if args.generator == "spack":
        generate_spack_matrix(args, experiment, " ".join(extra))


def generate_spack_matrix(args, experiment, command=None):
    """A spack matrix derives versions from spack, and prepares
    to generate commands (and metadata) to support a spack splice
    experiment
    """
    # Get versions of package
    versions = requests.get(
        "https://raw.githubusercontent.com/spack/packages/main/data/packages/%s.json"
        % experiment.package
    )
    if versions.status_code != 200:
        sys.exit("Failed to get package versions")
    versions = versions.json()
    versions = list(set([x["name"] for x in versions["versions"]]))

    # If we have a container, get compilers. Otherwise default to "all"
    labels = ["all"]

    if args.container:
        response = requests.get("https://crane.ggcr.dev/config/%s" % args.container)
        if response.status_code != 200:
            sys.exit(
                "Issue retrieving image config for % container: %s"
                % (args.container, response.reason)
            )

        config = response.json()
        labels = config["config"].get("Labels", {}).get("org.spack.compilers")
        labels = [x for x in labels.strip("|").split("|") if x]

    # We will build up a matrix of container and associated compilers
    matrix = []

    # Generate list of commands
    for version in versions:

        # versioned package
        package = "%s@%s" % (experiment.package, version)
        cmd = "spliced splice --package %s --splice %s --runner spack --replace %s --experiment %s" % (
            package,
            experiment.splice,
            experiment.replace,
            experiment.name,
        )
        if args.container:
            cmd = "%s --containers %s" % (cmd, args.container)
        if command:
            cmd = '%s --command "%s"' % (cmd, command)
        matrix.append(
            {
                "command": cmd,
                "package": package,
                "runner": "spack",
                "splice": experiment.splice,
                "replace": experiment.replace,
                "experiment": experiment.name,
                "container": args.container,
            }
        )

    # We can only get up to 256 max - select randomly
    if args.limit != 0 and len(matrix) >= args.limit:
        print(
            "Warning: original output is length %s and limit is set to %s jobs!"
            % (len(matrix), args.limit)
        )
        matrix = random.sample(matrix, args.limit)

    if args.outfile:
        utils.write_json(matrix, args.outfile)
    print("::set-output name=containers::%s\n" % json.dumps(matrix))
