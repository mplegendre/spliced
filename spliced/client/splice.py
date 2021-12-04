# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import sys
import json
import spliced.utils as utils


def main(args, parser, extra, subparser):

    if args.runner == "spack":
        run_spack_experiment(args, command=" ".join(extra))
    elif not args.runner:
        sys.exit("You must provide an experiment runner.")
    else:
        sys.exit("Runner %s is not recognized" % args.runner)


def run_spack_experiment(args, command):
    """
    Run a spack experiment, meaning we need to ensure spack is importable
    """
    add_spack_to_path()

    import spliced.experiment.spack

    experiment = spliced.experiment.spack.SpackExperiment()

    # We either load a config, or the arguments provided
    if args.config_yaml:
        experiment.load(args.config_yaml)
    else:
        experiment.init(
            args.package, args.splice, args.experiment, command, args.replace
        )

    # Perform the splice!
    experiment.run()

    # TODO can we run_parallel here as an option? And do splice -> predict as such
    # And make predictions
    experiment.predict(args.predictor)
    results = experiment.to_dict()

    if args.outfile:
        utils.write_json(results, args.outfile)
    else:
        print(json.dumps(results, indent=4))


def add_spack_to_path():
    """
    Find spack and add to path, allowing for import of spack modules
    """
    # Find path to spack install
    spack = utils.which("spack-python")
    if not spack["message"]:
        sys.exit("Make sure spack and spack-python are on your path for this runner.")

    # Find spack's location and its prefix, add libs and external libs
    spack_python = spack["message"]
    spack_prefix = os.path.dirname(os.path.dirname(spack_python))
    spack_lib_path = os.path.join(spack_prefix, "lib", "spack")
    spack_external_libs = os.path.join(spack_lib_path, "external")
    for path in [spack_lib_path, spack_external_libs]:
        sys.path.insert(0, path)
