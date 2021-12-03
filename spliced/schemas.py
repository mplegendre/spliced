# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

## Spliced config schema

schema_url = "https://json-schema.org/draft-07/schema/#"

properties = {
    "splice": {"type": "string"},
    "package": {"type": "string"},
    "replace": {"type": ["string", "null"]},
    "command": {"type": ["string", "null"]},
}

spliced_schema = {
    "$schema": schema_url,
    "title": "Spliced Schema",
    "type": "object",
    "required": [
        "package",
        "splice",
    ],
    "properties": properties,
    "additionalProperties": False,
}
