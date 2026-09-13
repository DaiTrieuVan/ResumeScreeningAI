# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import os


# Test discovery and ordinary API tests must never initialize or download a
# sentence-transformer. Dedicated embedding tests inject a deterministic model.
os.environ.setdefault("DISABLE_EMBEDDING_MODEL", "true")
