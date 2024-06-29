# Configuration

pyreminder is built around a simple, linear workflow:

- for each check
  - check the source
  - if the source has changed
    - enrich the data
    - for each destination
      - render the template
      - send the rendered template to the destination
  - schedule check to run again after a period of time

Each step is configured in `pyreminder.yml`:

```yaml
checks:
  - CHECK_NAME:
      source:
        type: SOURCE_TYPE
      enrichments:
        - type: ENRICHMENT_TYPE
      destinations:
        - type: DESTINATION_TYPE
          template: DESTINATION_TEMPLATE
      period: CHECK_PERIOD
```

