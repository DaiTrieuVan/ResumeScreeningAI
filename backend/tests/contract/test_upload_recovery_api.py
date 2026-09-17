# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from app.schemas.final_release import ManualRecoveryRequest


def test_manual_recovery_requires_substantive_verified_text_and_reason():
    payload = ManualRecoveryRequest(
        mode="VERIFIED_TEXT",
        verified_text="Verified Python experience from the scanned source.",
        reason="Human checked page one",
    )
    assert payload.mode == "VERIFIED_TEXT"
    assert len(payload.verified_text) >= 20
