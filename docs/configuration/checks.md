# Checks

Checks are executed at regular intervals. If the source in the check is triggered, it executes the rest of the workflow.

```yaml
checks:
  - console:
      source:
        type: reminder
      enrichments:
        - type: datetime
      destinations:
        - type: console
          template: "Hello, World!"
      period: 30s
      meta:
        - tag: my-meta-tag
      debug: true
```

`source`, `destination` and `period` are configured to establish how the check will proceed and are required. The following fields are optional
- `meta`, `enrichments`: see [Enrichments and Templates](../enrichments_and_templates)
- `debug`: if set to true, the check will always fire

