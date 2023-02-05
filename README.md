# Pyreminder
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/haondt/pyreminder/github-actions.yml)](https://github.com/haondt/pyreminder/actions/workflows/github-actions.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/haumea/pyreminder)](https://hub.docker.com/r/haumea/pyreminder/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/haondt/pyreminder)](https://github.com/haondt/pyreminder/releases/latest)


Pyreminder is a minimal tool for checking statuses and sending notifications. Inspired by [Kibitzr](https://kibitzr.github.io/) but meant to be simpler. Pyreminder is configured with a single yaml file:
```yaml
checks:
  - pyreminder:
      source:
        type: docker-hub
        namespace: haumea
        repository: pyreminder
        tag: latest
      destinations:
        - type: discord
          webhookURL: ${PYREMINDER_DISCORD_WEBHOOK_URL}
          color: 1ABC9C
          template: "Hooray! A new version of `${docker_hub__image}` was just released!"
      period: 1d
```
![image](https://user-images.githubusercontent.com/19233365/210116896-3c4c4dea-85f5-46a0-8934-38e13ebf56bb.png)

Check the [wiki](https://github.com/haondt/pyreminder/wiki/Installation) to get started.
