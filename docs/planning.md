# Trump Data Flow

## 1.0 Sourcing 

Individual feeds are queried based on the Feed's 'stype', sourcing_key and souring parameters.

- [ ] ORM
  - [x] Model
    - [x] string only parameters
    - [ ] dynamically typed parameters
    - [ ] Non-DateTime Index
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
      - [ ] CSV
        - [ ] Template
        - [ ] Extension
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
  - [ ] Non-parameter methods & High-priority
    - [x] Row-based Priority Fill (PRIORITY_FILL)
    - [ ] Feed-based First Available (...)
    - [ ] Feed-based Most Recent (...)
  - [ ] Parameter based methods (Eg. Feed-based with data as of 1 B.day, Row-based within 5% of Previous)
  - [ ] No parameter & Low-priority (Eg. Feed-based with data as of 1 B.day, Row-based within 5% of Previous)

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
