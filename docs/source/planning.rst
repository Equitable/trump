Planning
========

Trump is still in a planning stage.  Trump's initial priority is numeric and monotonic timeseries data,
but written with the future in mind to eventually work with any sortable object as data, and any object as an index.
Eliminating the monotonic assumption is a very low priority. 

The 0.1.0 release of Trump is planned to include the basics of the framework discussed above. 
A Web UI currently exists, but is outside the scope of this package until user demand justifies it's release.
A lighter-weight read-only API is also planned, but outside the scope of this package.

See doc/planning.md for the current state of the project.

Timing 
------

Finishing the planning phase should be finished by late-March 2015; the code base is under rapid expansion 
and changes.  Planning the testing framework is tentatively mid-April 2015, with the hopes of participating
in `Adopt py.test <http://pytest.org/latest/adopt.html>`_.  The first release is optimistically scheduled for early June 2015, with 
the fractions of the initial goals completed:

- Prioritization
  - Priority Index-based
  - Priority Feed-Based
  - Latest Available Feed-Based
- Modified
  - Override Index-based
  - Failsafe Index-based
- Verified  - Feed Compare Index-based
  - Feed Compare Feed-based
- Audited (Not Started)
- Aggregated
  - Mean
  - Median
  - Basic Pandas Functionality (Eg. pct_change())
- Customized
  - Framework ready
