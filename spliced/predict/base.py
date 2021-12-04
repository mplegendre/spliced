# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spliced.logger import logger
import spliced.utils as utils

import shlex
import os
import re


class Prediction:
    """
    A prediction is a base for assessing a Splice and making predictions.
    """

    def predict(self, splice):
        raise NotImplementedError

    def __str__(self):
        return str(self.__class__.__name__)


class Actual(Prediction):
    """
    Given a splice result with a command, get an actual result.
    """

    def predict(self, splice):
        if not splice.command:
            return

        # Check each binary to match the command
        executable = shlex.split(splice.command)[0]
        results = []
        for binary in splice.binaries:
            if binary.endswith(executable):
                cmd = "%s%s%s" % (os.path.dirname(binary), os.path.sep, splice.command)
                res = utils.run_command(cmd)
                res["prediction"] = True if res["return_code"] == 0 else False
                res["command"] = cmd
                results.append(res)

        splice.predictions["actual"] = results
