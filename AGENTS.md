# HTAG Data Pipeline — Codex Development Instructions

## 1. Purpose

This repository contains the HTAG property-market data pipeline.

The pipeline:

1. Extracts data from the HTAG API.
2. Stores raw API responses locally.
3. Cleans and transforms raw data.
4. Writes cleaned CSV files.
5. Uploads prepared data to Supabase.
6. Runs the pipeline through a central orchestration script.

The current implementation works, but parts of the code were generated quickly and are unnecessarily difficult to read.

The goal of this refactor is to improve:

* readability
* maintainability
* consistency
* separation of responsibilities
* naming
* testability
* error handling

The goal is **not** to redesign the pipeline architecture or change its existing business behavior unless explicitly requested.

---

# 2. Preserve the Existing Architecture

Keep the existing repository structure.

```text
htag_data_pipeline/
│
├── outbound/
│   ├── __init__.py
│   ├── __utils__.py
│   ├── create_sql_tables.sql
│   ├── endpoints.py
│   └── localities.py
│
├── pipelines/
│   ├── __init__.py
│   ├── clean.py
│   ├── ingest.py
│   └── upload.py
│
├── transformers/
│   ├── __init__.py
│   ├── __utils__.py
│   ├── localities.py
│   ├── market_demand.py
│   ├── market_endpoints.py
│   ├── market_registry.py
│   ├── market_supply.py
│   ├── market_trends_days_on_market.py
│   ├── market_trends_demand_profile.py
│   ├── market_trends_price.py
│   ├── market_trends_rent.py
│   └── market_trends_yield.py
│
├── config.py
├── endpoints.py
├── htag_client.py
├── json_storage.py
├── logging_utils.py
├── pipeline_config.py
├── pipeline_config.yml
├── README.md
└── run_htag_pipeline.py
```

Do not collapse these layers into one file.

Do not create a new architectural pattern unless explicitly requested.

---

# 3. Layer Responsibilities

Each layer must have a clear responsibility.

## `run_htag_pipeline.py`

Responsible only for orchestration.

It should:

* determine the run date
* load pipeline configuration
* initialize logging
* execute ingest, clean, and upload stages
* handle top-level pipeline failures
* provide clear progress logging

It should not contain:

* endpoint-specific transformations
* HTTP implementation details
* Supabase implementation details
* CSV cleaning logic
* large blocks of data transformation code

The main orchestration function should be readable from top to bottom.

A developer should be able to understand the complete execution sequence by reading this file.

---

## `pipelines/ingest.py`

Responsible for ingestion workflows.

It should coordinate:

```text
HTAG API
    ↓
raw JSON storage
```

It may call:

* `htag_client.py`
* `json_storage.py`
* endpoint configuration
* locality input files where required

It should not contain transformation logic.

---

## `pipelines/clean.py`

Responsible for cleaning workflows.

It should coordinate:

```text
raw JSON
    ↓
endpoint transformer
    ↓
clean CSV
```

It should:

* discover/load raw input
* select the correct transformer
* execute transformation
* write clean output
* log row counts

It should not duplicate transformer logic.

---

## `pipelines/upload.py`

Responsible for upload workflows.

It should coordinate:

```text
clean CSV
    ↓
outbound uploader
    ↓
Supabase
```

It should not contain:

* transformation logic
* API ingestion logic
* endpoint-specific cleaning logic

---

# 4. Transformer Design

Each endpoint should continue to have a dedicated transformer where endpoint-specific transformation rules exist.

Examples:

```text
market_trends_price.py
market_trends_rent.py
market_trends_yield.py
market_trends_days_on_market.py
market_trends_demand_profile.py
market_demand.py
market_supply.py
```

Each transformer should expose one obvious public transformation function.

Preferred pattern:

```python
def transform_market_trends_price(raw_data: list[dict]) -> pd.DataFrame:
    """
    Transform raw HTAG market price trend records into the
    clean schema expected by the pipeline.
    """
```

Avoid exposing many tiny public functions unless they are independently reusable.

Endpoint-specific business rules belong in the endpoint transformer.

Shared transformation behavior belongs in:

```text
transformers/market_endpoints.py
```

Generic low-level helpers belong in:

```text
transformers/__utils__.py
```

---

# 5. Utility Function Rules

Utility modules must contain genuinely reusable functions.

Examples of appropriate utilities:

* finding raw files
* loading JSON files
* combining raw versions
* normalizing dates
* writing CSV files
* validating required columns
* resolving data directories
* converting HTAG paths to local folder names
* generic batching helpers

Do not move business logic into utility modules simply to make another file smaller.

---

# 6. Do Not Create Pass-Through Wrapper Functions

Avoid functions whose only purpose is to call another function with the same arguments.

Bad:

```python
# utils.py

def read_json_files(path):
    ...
```

```python
# clean.py

def load_json_files(path):
    return read_json_files(path)
```

Then:

```python
data = load_json_files(path)
```

This adds another level of indirection without adding any value.

Prefer:

```python
data = read_json_files(path)
```

Create a wrapper only when it provides real pipeline behavior.

For example:

```python
def load_endpoint_raw_data(endpoint, run_date):
    raw_files = discover_raw_files(
        endpoint=endpoint,
        run_date=run_date,
    )

    if not raw_files:
        raise FileNotFoundError(
            f"No raw files found for {endpoint['path']} "
            f"for run date {run_date}"
        )

    logger.info(
        "Loading %s raw files for %s",
        len(raw_files),
        endpoint["path"],
    )

    return read_raw_files(raw_files)
```

This wrapper is acceptable because it adds:

* validation
* pipeline semantics
* logging
* endpoint context

---

# 7. Avoid Functions Calling Functions Calling Functions

Do not create unnecessary call chains such as:

```text
run_clean()
    ↓
clean_data()
    ↓
prepare_data()
    ↓
load_data()
    ↓
read_data()
    ↓
read_json()
```

when most functions simply forward arguments.

Prefer shallow call structures.

A typical pipeline stage should usually be understandable within approximately 2–3 levels of function calls.

Preferred:

```text
clean_market_endpoint()
    ├── load_raw_versions()
    ├── transform_endpoint()
    └── write_clean_csv()
```

---

# 8. Functions Must Have One Clear Responsibility

Functions should perform one meaningful operation.

Good:

```python
def load_raw_versions(...):
    ...

def transform_market_trends_price(...):
    ...

def write_clean_csv(...):
    ...
```

Avoid very large functions that:

* load files
* transform records
* upload data
* handle HTTP calls
* manage retries
* manipulate paths

all in one place.

At the same time, do not over-split simple logic into many 3-line functions.

Use judgment.

The objective is readability, not maximizing the number of functions.

---

# 9. Prefer Explicit Code Over Clever Code

Favor readable Python.

Prefer:

```python
if clean_enabled:
    clean_market_endpoint(
        endpoint=endpoint,
        run_date=run_date,
        data_dir=data_dir,
    )
```

over compressed or heavily abstracted patterns that require tracing several files.

Avoid:

* unnecessary lambdas
* nested comprehensions
* deeply nested ternary expressions
* dynamic function generation
* unnecessary decorators
* unnecessary metaprogramming
* clever one-line transformations

---

# 10. Naming

Names should explain intent.

Use names such as:

```python
raw_records
clean_dataframe
endpoint_config
run_date
locality_ids
response_payload
clean_output_path
conflict_columns
```

Avoid names such as:

```python
data1
tmp
res
obj
x
d
items2
output_final_new
```

Boolean variables should clearly describe a condition:

```python
ingest_enabled
clean_enabled
upload_enabled
has_area_ids
is_trend_endpoint
```

---

# 11. Function Arguments

Prefer keyword arguments for pipeline-level calls.

Good:

```python
clean_market_endpoint(
    endpoint=endpoint,
    run_date=run_date,
    data_dir=data_dir,
)
```

Avoid:

```python
clean_market_endpoint(endpoint, run_date, data_dir, True, False)
```

Do not pass the same configuration through many unnecessary wrapper layers.

---

# 12. Docstrings

Public or non-obvious functions should have concise docstrings.

Example:

```python
def transform_market_supply(raw_data: list[dict]) -> pd.DataFrame:
    """
    Transform HTAG market supply records into the clean
    schema expected by Supabase.
    """
```

Do not write docstrings that simply repeat the function name.

Bad:

```python
def clean_data(data):
    """Clean data."""
```

---

# 13. Comments

Comments should explain **why**, not restate **what** the code already says.

Good:

```python
# Demand and supply endpoints store only the latest observation,
# unlike trend endpoints which retain a rolling history window.
```

Bad:

```python
# Loop through endpoints
for endpoint in endpoints:
```

---

# 14. Error Handling

Do not silently ignore errors.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

Errors should include useful context:

```python
raise RuntimeError(
    f"Failed to clean endpoint {endpoint['path']} "
    f"for run date {run_date}"
) from exc
```

Log:

* endpoint
* run date
* input path where useful
* HTTP status where applicable
* row counts
* output path

Do not log secrets.

Never log:

* HTAG API keys
* Supabase keys
* environment credentials

---

# 15. Logging Style

Use structured, concise logging.

Preferred:

```python
logger.info(
    "Cleaning endpoint=%s run_date=%s",
    endpoint["path"],
    run_date,
)
```

and:

```python
logger.info(
    "Clean complete endpoint=%s rows=%s output=%s",
    endpoint["path"],
    len(clean_df),
    output_path,
)
```

Avoid excessive logs from tiny helper functions.

Pipeline-level functions should be primarily responsible for progress logging.

---

# 16. Endpoint Configuration

`endpoints.py` remains the authoritative source of HTAG endpoint behavior.

Do not duplicate endpoint metadata in transformer files.

Endpoint configuration may include:

* path
* table
* request parameters
* pagination settings
* area-ID batching configuration
* Supabase conflict columns
* upload columns

Transformer modules should receive configuration rather than redefine it unnecessarily.

---

# 17. Pipeline Configuration

`pipeline_config.yml` remains responsible for stage switches.

Each dataset may independently control:

```yaml
ingest: Y
clean: Y
upload: Y
```

Do not move these switches into Python constants.

The global Python `upload=False` safety behavior must remain intact.

---

# 18. Preserve Existing Pipeline Behavior

During refactoring, do not intentionally change:

* endpoint paths
* API parameters
* pagination behavior
* Supabase table names
* conflict keys
* clean CSV schemas
* folder naming
* raw file versioning
* run-date behavior
* pipeline configuration behavior
* ingestion frequency assumptions
* 13-month rolling history rules
* latest-value behavior for demand and supply

unless explicitly requested.

A readability refactor must not silently alter data.

---

# 19. HTAG Business Rules to Preserve

The current pipeline includes the following business requirements.

## Refresh schedule

Data is designed to refresh every 30 days.

## Trend endpoints

Relevant trend endpoints retain approximately 13 months of history.

Examples include:

* market price trends
* market rent trends
* market yield trends
* demand profile trends
* days-on-market trends

## Current-value endpoints

The following endpoints retain the latest required values rather than historical trend records:

* `/markets/demand`
* `/markets/supply`

## Days on Market

Days-on-market data must use:

```text
/markets/trends/days-on-market
```

Do not replace this with another HTAG endpoint.

---

# 20. Raw Data Must Remain Immutable

Raw API responses should not be overwritten.

Continue using versioned raw storage such as:

```text
raw/
├── v001/
│   └── response.json
├── v002/
│   └── response.json
└── ...
```

Cleaning may combine raw versions where required.

Clean output may overwrite:

```text
clean/response.csv
```

for the selected run date.

---

# 21. Data Flow Must Stay Obvious

A developer reading the pipeline should be able to recognize this flow immediately:

```text
HTAG API
   ↓
Ingest
   ↓
Raw JSON
   ↓
Clean
   ↓
Endpoint Transformer
   ↓
Clean CSV
   ↓
Upload
   ↓
Supabase
```

Do not obscure this flow through excessive abstraction.

---

# 22. Import Rules

Prefer direct and explicit imports.

Good:

```python
from transformers.__utils__ import load_raw_versions
from transformers.market_registry import get_transformer
```

Avoid wildcard imports:

```python
from transformers.__utils__ import *
```

Avoid circular dependencies.

Utilities must not import pipeline modules.

Expected dependency direction:

```text
run_htag_pipeline
        ↓
pipelines
        ↓
transformers / outbound
        ↓
shared low-level modules
```

Do not create dependencies going upward through these layers.

---

# 23. `__init__.py`

Keep `__init__.py` files lightweight.

Do not use them to hide important execution behavior.

Avoid excessive function re-exporting when it makes it difficult to identify where functions are implemented.

Prefer importing important pipeline functions from their real module.

---

# 24. Avoid Premature Generic Abstractions

Do not create generic frameworks such as:

```python
BasePipeline
BaseTransformer
AbstractHTAGProcessor
PipelineFactory
TransformerFactory
DataProcessorManager
```

unless there is a concrete need.

Simple functions and dictionaries are preferred for this project.

The project is small enough that explicit code is easier to maintain.

---

# 25. Endpoint Registry

Continue using the transformer registry to map endpoint paths to transformer functions.

Preferred concept:

```python
TRANSFORMERS = {
    "/markets/trends/price": transform_market_trends_price,
    "/markets/trends/rent": transform_market_trends_rent,
    "/markets/trends/yield": transform_market_trends_yield,
}
```

The lookup should remain straightforward.

Do not introduce reflection or dynamic module imports unless required.

---

# 26. Refactoring Procedure

When refactoring existing code, use the following process.

### Step 1 — Understand

Before editing a module:

* identify what it currently does
* identify its callers
* identify functions it calls
* identify expected inputs
* identify expected outputs
* identify side effects

Do not refactor code based only on its appearance.

### Step 2 — Remove unnecessary indirection

Look specifically for:

* wrapper functions that only call another function
* duplicate utilities
* duplicated validation
* duplicated path construction
* nested helper chains
* dead code
* unused imports

### Step 3 — Improve naming

Rename variables and functions where names are unclear.

### Step 4 — Simplify control flow

Prefer:

* early returns
* clear validation
* small logical sections

Avoid deeply nested `if` blocks.

### Step 5 — Preserve outputs

Verify that the refactored version produces equivalent outputs before moving to the next module.

---

# 27. Refactor Incrementally

Do not refactor the entire repository in one large change.

Use this order.

## Phase 1

Refactor:

```text
pipelines/clean.py
transformers/__utils__.py
```

Focus specifically on eliminating unnecessary wrapper functions.

## Phase 2

Refactor:

```text
pipelines/ingest.py
htag_client.py
json_storage.py
```

## Phase 3

Refactor endpoint transformers individually:

```text
market_trends_price.py
market_trends_rent.py
market_trends_yield.py
market_trends_days_on_market.py
market_trends_demand_profile.py
market_demand.py
market_supply.py
```

## Phase 4

Refactor:

```text
pipelines/upload.py
outbound/__utils__.py
outbound/localities.py
outbound/endpoints.py
```

## Phase 5

Refactor:

```text
run_htag_pipeline.py
pipeline_config.py
endpoints.py
```

Only after lower-level modules have stabilized.

---

# 28. Do Not Make Large Unrequested Changes

When asked to refactor one module:

* modify that module
* modify directly related helpers only where necessary
* avoid unrelated cleanup across the repository

Do not rename dozens of public functions in one operation.

Do not reorganize directories without explicit approval.

---

# 29. Before Removing a Function

Before deleting or merging a function:

1. Search the repository for all references.
2. Confirm no other module depends on it.
3. Move any meaningful behavior to the appropriate remaining function.
4. Update imports.
5. Run relevant tests or pipeline validation.

Do not assume a function is unused.

---

# 30. Validation After Refactoring

After each meaningful refactor, verify:

* imports succeed
* pipeline configuration loads
* endpoint registry resolves correctly
* existing raw data can be cleaned
* output row counts are reasonable
* clean CSV columns remain unchanged
* Supabase mapping remains unchanged
* no credentials are exposed
* no unnecessary API calls were introduced

When possible, compare:

```text
before row count
after row count

before columns
after columns

before sample records
after sample records
```

A pure refactor should produce equivalent results.

---

# 31. Code Formatting

Follow standard Python formatting.

Use:

* 4-space indentation
* descriptive snake_case names
* reasonable line lengths
* blank lines between logical sections
* trailing commas for multi-line function calls where appropriate

Preferred:

```python
clean_df = transform_endpoint(
    raw_data=raw_data,
    endpoint=endpoint,
    run_date=run_date,
)
```

instead of:

```python
clean_df = transform_endpoint(raw_data,endpoint,run_date)
```

---

# 32. Type Hints

Use type hints where they make interfaces clearer.

Example:

```python
from pathlib import Path

def get_clean_output_path(
    data_dir: Path,
    run_date: str,
    endpoint_path: str,
) -> Path:
    ...
```

Do not add extremely complicated typing purely for completeness.

Readability takes priority.

---

# 33. Main Refactoring Principle

Whenever choosing between two implementations, prefer the implementation that makes it easiest for another Python developer to answer:

1. Where does this data come from?
2. What transformation happens to it?
3. Where is the result written?
4. Which function owns this business rule?
5. What happens when this step fails?

If answering one of these questions requires jumping through many wrapper functions, simplify the implementation.

---

# 34. Definition of Done

A refactored module is considered complete when:

* existing behavior is preserved
* function names clearly describe intent
* unnecessary wrapper functions are removed
* duplicate helper logic is removed
* functions have clear responsibilities
* nesting is reasonable
* logging is understandable
* errors contain useful context
* imports remain simple
* no secrets are logged
* the module can be understood without tracing unnecessary function chains
* pipeline output remains equivalent to the pre-refactor output

The priority order is:

```text
Correctness
    ↓
Readability
    ↓
Maintainability
    ↓
Reusability
    ↓
Abstraction
```

Never sacrifice readability merely to make code more generic.
