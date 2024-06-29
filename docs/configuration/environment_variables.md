# Environment Variables

pyreminder supports environment variables everywhere except inside templates. It is recommended to store secrets in environment variables rather than directly in `pyreminder.yml`. If you need to use an environment variable in a template, store it in a meta tag and reference the tag in the template.

## Example

```yaml title='docker-compose.yml'
services:
  pyreminder:
    image: haumea/pyreminder:latest
    volumes:
      - ./pyreminder.yml:/config/pyreminder.yml
      - pyreminder_data:/data
    environment:
      PYREMINDER_SUPER_SECRET_LINK: "https://google.com"

volumes:
  pyreminder_data:
```

```yaml title='pyreminder.yml'
checks:
  - timestamp:
      source:
        type: reminder
      destinations:
        - type: console
          template: "Here is your super secret link: ${meta__link}"
      meta:
        link: ${PYREMINDER_SUPER_SECRET_LINK}
      period: 30s
```

#### output
```
Here is your super secret link: https://google.com
```

