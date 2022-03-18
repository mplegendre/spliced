# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spliced.predict.base import Prediction
from .smeagle import SmeagleRunner
from spliced.logger import logger
import itertools
import os


class SmeaglePrediction(Prediction):
    def predict(self, splice):
        """
        Run smeagle to add to the predictions
        """
        # If no splice libs OR no tools, cut out early
        if not splice.libs:
            return

        # Create a smeagle runner!
        self.smeagle = SmeagleRunner()
        if not self.smeagle.check():
            logger.warning("Smeagle is missing dependencies to run, skipping.")
            return

        # Case 1: We ONLY have a list of libs that were spliced.
        if (
            "spliced" in splice.libs
            and "original" in splice.libs
            and splice.libs["spliced"]
        ):
            self.test_equivalent_libs(splice, splice.libs["spliced"])

        # Case 2: We are mocking a splice, and we have TWO sets of libs: some original, and some to replace with
        elif "dep" in splice.libs and "replace" in splice.libs:
            self.test_different_libs(splice, splice.libs["dep"], splice.libs["replace"])

    def test_different_libs(self, splice, original_libs, replace_libs):
        """
        Splicing in a totally different lib into itself
        """
        # Flatten original and replacement libs
        original_libs = list(itertools.chain(*[x["paths"] for x in original_libs]))
        replace_libs = list(itertools.chain(*[x["paths"] for x in replace_libs]))

        # Assemble a set of predictions using abicompat
        predictions = []
        for original_lib in original_libs:
            for replace_lib in replace_libs:
                res = self.smeagle.stability_test(original_lib, replace_lib)
                res["splice_type"] = "different_lib"
                predictions.append(res)

        if predictions:
            splice.predictions["smeagle"] = predictions

    def test_equivalent_libs(self, splice, libs):
        """
        Splicing a different version of the "same" lib into itself
        """
        # Flatten original libs into flat list
        original_libs = list(
            itertools.chain(*[x["paths"] for x in splice.libs.get("original", [])])
        )

        # Assemble a set of predictions
        predictions = []
        for libset in libs:
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
                        "Warning, original comparison library not found for %s, required for abidiff."
                        % lib
                    )
                    continue

                # The best we can do is compare all contender matches
                for original in originals:
                    res = self.smeagle.stability_test(original, lib)
                    res["splice_type"] = "same_lib"
                    predictions.append(res)

        if predictions:
            splice.predictions["smeagle"] = predictions
            print(splice.predictions)
