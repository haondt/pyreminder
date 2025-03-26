# Enrichments and Templates

Templates allow you to format the output of a source before it is sent to a destination. Enrichments allow you to add data sources for your templates. 


## Defining templates

A template can be specified in the description of a destination:

```yaml
checks:
  - console:
      source:
        type: reminder
      destinations:
        - type: console
          template: "Hello, World!"
      period: 30s
```

Templates can also be specified separately, so you can use the same template in multiple destinations
```yaml
checks:
  - console:
      source:
        type: reminder
      destinations:
        - type: console
          template: my-template
      period: 30s

templates:
  my-template: |
    Hello, World!
```

## Template Variables

When rendering the template, you can use variables to dynamically set the output of the template. Templates are rendered using python [template strings](https://docs.python.org/3/library/string.html#template-strings). The available keys to the template will depend on the configuration of the check.

### Default variables

These variables are added to every check

- `check__name`: the name of the check

### Meta variables

Optionally, you can specify meta values in the check. This is useful for passing environment variables to your template, or tagging your check with a value to show in the output.

The variable in the template will be prepended with `meta__`. Example:

**pyreminder.yaml**
```yaml
checks:
  - console_check:
      source:
        type: reminder
      destinations:
        - type: console
          template: "This was rendered by ${check__name} version ${meta__version}"
      meta:
         version: 1.2.3
      period: 30s
```

**output**
```
This was rendered by console_check version 1.2.3
```

## Sources and Enrichments

The source will also make some variables available to the template. If a source is added as an enrichment, it will make its variables available without affecting the result of the check. See [Sources](../sources)

