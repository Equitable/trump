# Trump Data Flow

## 1.0 Sourcing 

Individual feeds are queried based on the Feed's 'stype', sourcing_key and souring parameters.

- [ ] ORM
  - [x] Model
    - [x] string only parameters
    - [ ] dynamically typed parameters
    - [X] Non-DateTime Index
    - [ ] Non-Float Data
  - [ ] API
- [ ] Templates & Extensions
  - [x] Model
  - [ ] API
  - [ ] Support For Minimum Compliment
    - [x] Quandl
      - [x] Template
      - [x] Extension
    - [x] DBAPI 2.0
      - [x] Primary Templates
      - [x] Primary Extensions
      - [ ] Secondary Templates
      - [ ] Secondary Extensions
    - [ ] psycopg2
      - [ ] Templates
      - [ ] Extensions
    - [ ] SQLA
      - [x] Template
      - [ ] Extension
    - [ ] pandas.io
       - [X] DataReader
        - [X] Template
        - [X] Extension     
      - [X] CSV
        - [X] Template
        - [X] Extension
      - [ ] Excel
        - [ ] Template
        - [ ] Extension
      - [ ] JSON
        - [ ] Template
        - [ ] Extension
      - [ ] HTML

# 2.0 Feed Munging

Each munging step is performed in order, according to it's 'mtype', and keyword arguments.

- [ ] ORM
  - [ ] Model
    - [x] string only parameters
    - [ ] dynamically typed parameters
  - [ ] API
- [ ] Templates & Extensions
  - [ ] Trump Based Munging Extensions
  - [ ] Pandas Based Munging
    - [X] Attribute-based math (Eg. .abs(), .pct_change(), .add())
    - [ ] Attribute & lambda based math (Eg. .apply(), .groupby())
    - [ ] Mutable munging (eg. .reindex(), .dropna())
    - [ ] Self-referential (eg. .duplicated(), )
    - [X] Non-attribute math (eg. rolling_mean(), )
    - [ ] Non-attribute & lambda based math (eg. rolling_apply(), )

# 3.0 Feed Aggregation

The Symbol's final column is calculated according to the symbol's aggregation method.

- [ ] ORM
  - [ ] Model
    - [x] string only parameters
    - [ ] dynamically typed parameters
  - [ ] API
- [ ] Templates & Extensions
  - [X] Non-parameter methods & High-priority
    - [x] Row-based Priority Fill (PRIORITY_FILL)
    - [X] Feed-based First Available (...)
    - [X] Feed-based Most Recent (...)
  - [ ] Parameter based methods (Eg. Feed-based with data as of 1 B.day, Row-based within 5% of Previous)
  - [ ] No parameter & Low-priority (Eg. Feed-based with data as of 1 B.day, Row-based within 5% of Previous)
- [X] Dynamically Typed Override & FailSafe index and data values.

# 4.0 Symbol Munging

The last processing step is to munge the final series. 

- [ ] ORM
  - [ ] Model
    - [ ] string only parameters
    - [ ] dynamically typed parameters
  - [ ] API
- [ ] Templates & Extensions
  - [ ] Trump Based Munging Extensions
  - [ ] Pandas Based Munging
    - [ ] Attribute-based math (Eg. .abs(), .pct_change(), .add())
    - [ ] Attribute & lambda based math (Eg. .apply(), .groupby())
    - [ ] Mutable munging (eg. .reindex(), .dropna())
    - [ ] Self-referential (eg. .duplicated(), )
    - [ ] Non-attribute math (eg. rolling_mean(), )
    - [ ] Non-attribute & lambda based math (eg. rolling_apply(), )

# Validity

Optionally, the validity checks can be executed before and after each of the above steps.
- [ ] ORM
  - [ ] Model
    - [ ] string only parameters
    - [ ] dynamically typed parameters
  - [ ] API
- [ ] Templates & Extensions
  - [ ] Existence Checking
    - [ ] Frequency
    - [ ] NaNs
    - [ ] Time of Day
    - [ ] Length-Based
  - [ ] Value Checking
    - [ ] Moving Average based
  - [ ] Feed Matching
  - [ ] Dropped Data
  - [ ] Duplicated Data
  - [ ] ???
- [ ] Reporting
  - [ ] HTML
  - [ ] DataFrame

# Checks & Validity Objects

## ValidityResult Object

## FeedReport

## SymbolReport

## ValidityInstruction

ValidityInstruction objects contain information used to check a Symbol's data.  The end application
should never "see" the data from the individual feeds, however a validity check can look at for the purposes of checking the
validity of the final.

A symbol has a single .isvalid() method, which will run the checks associated with each ValidityInstruction Object.
The function returns a ValidityResult object.  The ValidtyResult object can be compared against a boolean, in an all-or-nothing way,
or it can be converted to a list of booleans, a dictionary of booleans where the keys are the names of the individual checks,
or a more advanced object which is a dictionary keyed by the test name, but the value returned is an object decided by the test.

Examples of Validity Checks might be:

- Length
- MissingData (gaps)
- Recency [has there been data in the last X days]
- Today [is there a datapoint for today]
- Last-Close-to-Others
- FrequencyAutoDetectable
- StandardDeviationLevel (eg. Realized Volatility)
- DeviationFromMovingAverage
- FeedLengthCompare
- FeedDeviationCompare
- CheckExistence

## FeedHandle & SymbolHandle

A *Handle object is attached to each Symbol, and Feed, one-to-one.  So, a Symbol with 3 Feeds, would have 1 SymbolHandle, and 3 FeedHandle objects.

It contains instructions about how to handle common exceptions raised during the caching of an individual Feeds, or the aggregation of a Symbol.

Trump has default settings for each type of failure, that get read from the config file when a SymbolManager is instantiated.
The defaults stored in the config, get attached permanently to the Feed or Symbol upon instatiation.  One can update them,
at any point.
