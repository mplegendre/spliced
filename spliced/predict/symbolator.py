# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from .base import Prediction
from spliced.logger import logger
from symbolator.asp import PyclingoDriver, ABIGlobalSolverSetup, ABICompatSolverSetup
from symbolator.facts import get_facts
from symbolator.corpus import JsonCorpusLoader, Corpus

import os
import re


class SymbolatorPrediction(Prediction):
    def predict(self, splice):
        """
        Run symbolator to add to the predictions
        """
        # A corpora cache to not derive again if we already have
        corpora = {}

        # Create a set of predictions for each spliced binary / lib combination
        predictions = []
        for binary in splice.binaries.get("spliced", []):

            # Cache the corpora if we don't have it yet
            if binary not in corpora:
                corpora[binary] = get_corpus(binary)

            for libset in splice.libs.get("spliced", []):
                for lib in libset["paths"]:

                    # Also cache the lib if we don't have it yet
                    if lib not in corpora:
                        corpora[lib] = get_corpus(lib)

                    # Make the splice prediction with symbolator
                    sym_result = run_symbols_splice(corpora[binary], corpora[lib])
                    sym_result["binary"] = binary
                    sym_result["lib"] = lib
                    sym_result["prediction"] = (
                        True if not sym_result["missing"] else False
                    )
                    predictions.append(sym_result)

        if predictions:
            splice.predictions["symbolator"] = predictions
            print(splice.predictions)


def run_symbol_solver(corpora):
    """
    A helper function to run the symbol solver.
    """
    driver = PyclingoDriver()
    setup = ABIGlobalSolverSetup()
    return driver.solve(
        setup,
        corpora,
        dump=False,
        logic_programs=get_facts("missing_symbols.lp"),
        facts_only=False,
        # Loading from json already includes system libs
        system_libs=False,
    )


def get_corpus(path):
    """
    Given a path, generate a corpus
    """
    setup = ABICompatSolverSetup()
    corpus = Corpus(path)
    return setup.get_json(corpus, system_libs=True, globals_only=True)


def run_symbols_splice(A, B):
    """
    Given two results, each a corpora with json values, perform a splice
    """
    result = {
        "missing": [],
        "selected": [],
    }

    # Spliced libraries will be added as corpora here
    loader = JsonCorpusLoader()
    loader.load(A)
    corpora = loader.get_lookup()

    # original set of symbols without splice
    corpora_result = run_symbol_solver(list(corpora.values()))

    # Now load the splices separately, and select what we need
    splice_loader = JsonCorpusLoader()
    splice_loader.load(B)
    splices = splice_loader.get_lookup()

    # If we have the library in corpora, delete it, add spliced libraries
    # E.g., libz.so.1.2.8 is just "libz" and will be replaced by anything with the same prefix
    corpora_lookup = {key.split(".")[0]: corp for key, corp in corpora.items()}
    splices_lookup = {key.split(".")[0]: corp for key, corp in splices.items()}

    # Keep a lookup of libraries names
    corpora_libnames = {key.split(".")[0]: key for key, _ in corpora.items()}
    splices_libnames = {key.split(".")[0]: key for key, _ in splices.items()}

    # Splices selected
    selected = []

    # Here we match based on the top level name, and add splices that match
    # (this assumes that if a lib is part of a splice corpus set but not included, we don't add it)
    for lib, corp in splices_lookup.items():

        # ONLY splice in those known
        if lib in corpora_lookup:

            # Library A was spliced in place of Library B
            selected.append([splices_libnames[lib], corpora_libnames[lib]])
            corpora_lookup[lib] = corp

    spliced_result = run_symbol_solver(list(corpora_lookup.values()))

    # Compare sets of missing symbols
    result_missing = [
        "%s %s" % (os.path.basename(x[0]).split(".")[0], x[1])
        for x in corpora_result.answers.get("missing_symbols", [])
    ]
    spliced_missing = [
        "%s %s" % (os.path.basename(x[0]).split(".")[0], x[1])
        for x in spliced_result.answers.get("missing_symbols", [])
    ]

    # these are new missing symbols after the splice
    missing = [x for x in spliced_missing if x not in result_missing]
    result["missing"] = missing
    result["selected"] = selected
    return result
