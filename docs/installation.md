The recommended way to run pyreminder is with docker compose. pyreminder requires a directory at `/data` for state storage and a configuration file mounted at `/config/pyreminder.yml`.
A pre-built docker image for pyreminder is available.

```
# from docker hub
docker pull haumea/pyreminder
# from gitlab
docker pull registry.gitlab.com/haondt/cicd/registry/haumea
```

## Example configuration

Here is an example that will print the current time (in utc) to the console every 30 seconds

```yaml title='docker-compose.yml'
services:
  pyreminder:
    image: haumea/pyreminder:latest
    volumes:
      - ./pyreminder.yml:/config/pyreminder.yml
      - pyreminder_data:/data

volumes:
  pyreminder_data:
```

```yaml title='pyreminder.yml'
checks:
  - timestamp:
      source:
        type: reminder
      enrichments:
        - type: datetime
      destinations:
        - type: console
          template: It is currently ${datetime__time_short}
      period: 30s
```

#### output
```
timestamp: It is currently 3:25 PM
timestamp: It is currently 3:26 PM
timestamp: It is currently 3:26 PM
timestamp: It is currently 3:27 PM
```
