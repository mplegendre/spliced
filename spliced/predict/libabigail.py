# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from .base import Prediction
from spliced.logger import logger
import spliced.utils as utils
import itertools

import os
import re


def add_to_path(path):
    path = "%s:%s" % (path, os.environ["PATH"])
    os.putenv("PATH", path)
    os.environ["PATH"] = path


class LibabigailPrediction(Prediction):
    def predict(self, splice):
        """
        Run libabigail to add to the predictions
        """
        # If no splice libs, cut out early
        if not splice.libs:
            return

        # First effort - do we have abicompat on the path?
        abicompat = utils.which("abicompat")
        if not abicompat["message"]:
            logger.warning("abicompat not found on path, will look for spack instead.")

            # Try getting from spack
            try:
                utils.add_spack_to_path()
                import spack.store

                installed_specs = spack.store.db.query("libabigail")
                if not installed_specs:
                    import spack.spec

                    abi = spack.spec.Spec("libabigail")
                    abi.concretize()
                    abi.package.do_install(force=True)
                else:
                    abi = installed_specs[0]

                add_to_path(os.path.join(abi.prefix, "bin"))
                abicompat = utils.which("abicompat")

            except:
                logger.error(
                    "You must either have abicompat (libabigail) on the path, or spack."
                )
                return

        if not abicompat["message"]:
            logger.error(
                "You must either have abicompat (libabigail) on the path, or spack."
            )
            return

        # This is the executable path
        abicompat = abicompat["message"]

        # Flatten original libs into flat list
        original_libs = list(
            itertools.chain(*[x["paths"] for x in splice.libs.get("original", [])])
        )

        # Assemble a set of predictions
        predictions = []
        for binary in splice.binaries.get("spliced", []):
            for libset in splice.libs.get("spliced", []):
                for lib in libset["paths"]:

                    # Try to match libraries based on prefix (versioning is likely to change)
                    libprefix = os.path.basename(lib).split(".")[0]

                    # Find an original library path with the same prefix
                    originals = [
                        x
                        for x in original_libs
                        if os.path.basename(x).startswith(libprefix)
                    ]
                    if not originals:
                        logger.warning(
                            "Warning, original comparison library not found for %s, required for abicompat."
                            % lib
                        )
                        continue

                    # The best we can do is compare all contender matches
                    for original in originals:

                        # Run abicompat to make a prediction
                        res = utils.run_command("%s %s %s" % (abicompat, original, lib))
                        res["binary"] = binary

                        # The spliced lib and original
                        res["lib"] = lib
                        res["original_lib"] = lib

                        # If there is a libabigail output, print to see
                        if res["message"] != "":
                            print(res["message"])
                        res["prediction"] = (
                            res["message"] == "" and res["return_code"] == 0
                        )
                        predictions.append(res)

        if predictions:
            splice.predictions["libabigail"] = predictions
            print(splice.predictions)
