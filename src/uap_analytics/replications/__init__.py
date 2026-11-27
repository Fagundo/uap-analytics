"""Replications of the data repository's population tests, reading only the combined export.

The data repository (uap-data) first ran these tests on its own loaders. They moved here (refactor Phase 6) so
that every statistical test lives in one analytics repository and reads the same versioned export as the
registered hypotheses. Each is a labelled replication: same method, same inputs, checked number for number
against the original outputs (``tests/parity/original_analyses_reference.json``) before any new use.

  * ``programs``: do sightings cluster near classified flight programs in space and time? (shuffle tests)
  * ``nuclear``: do reports rise in the days after nuclear tests? (event-window test with shifted series)
  * ``bluebook``: did Blue Book's conclusions shift when the spy planes began flying? (share-shift test)

``inputs`` is the only module that reads the export; ``common`` holds the shared places, dates and statistics.
"""
