"""Do sightings cluster near classified flight programs in space and time? (replication)

  * ``catalog``: programs, their windows, states and sites (the export's flight_programs layer)
  * ``sightings``: one sighting to test
  * ``shuffle``: the shuffle tests, by state (``CoincidenceTest``) and by distance (``ProximityTest``)
  * ``trend``: each site's share of reports year by year
"""
