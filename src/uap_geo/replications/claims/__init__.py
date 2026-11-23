"""Checking the explanations offered for famous cases against physics and their own stated facts (replication).

  * ``catalog``: cases and claims (the export's datasets/case_claims.json)
  * ``checks``: one check per kind of explanation (balloon, reentry, bolide, planet, beacon, flare)
  * ``sky``: low-precision Sun and planet positions
  * ``screen``: every bright planet or star up at a case's time and place, tested like a claim
  * ``report``: runs the checks and finds each case among the released files' incidents
"""
