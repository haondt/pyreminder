# Sources

Sources will check a value and trigger the rest of the workflow if the value has changed. If a source is added as an enrichment to a check, it will just make its variables available to the template renderer. See [enrichments and templates](../enrichments_and_templates) for more info.


## Reminder
```yaml
checks:
  - reminder:
      source:
        type: reminder
      destinations:
        - type: console
          template: "Good morning!"
      period: 1d
```

- config: none
- fires: always
- variables: none

## Get Request
```yaml
checks:
  - get-request:
      source:
        type: get-request
        url: https://google.com/
        parser: regex
        parseKey: <[^>]+>
      destinations:
        - type: console
          template: "The first tag has changed! It is now ${get_request__text}"
      period: 1d
```

- config:
    - `url`: url to send a `GET` request to
    - `parser`: can be `json` or `regex`, specifies the method for parsing the response body
    - `parseKey`: for `json`, this will be a json path (e.g. `foo.bar[2].baz`) to apply to the response body. For `regex`, this is just a regular expression to apply to the response body.
- fires: when the value extracted by the `parseKey` changes
- variables:
    - `get_request__text`: the value extracted by the `parseKey`

## Datetime

```yaml
checks:
  - reminder:
      source:
        type: reminder
      enrichments:
        - type: datetime
          tz: America/Edmonton
          format: d M y
      destinations:
        - type: console
          template: "${datetime__formatted}"
      period: 30s
```

- config:
    - `tz`: optional, timezone
    - `format`: optional, format for `datetime__formatted` variable
- fires: never (best used as an enrichment)
- variables:
    - `datetime__date_short`: date in the format 2000/04/20
    - `datetime__date_long`: date in the format April 4, 2000
    - `datetime__date_full`: date in the format Tuesday, April 4, 2000
    - `datetime__time_short`: time in the format 4:00 PM
    - `datetime__time_long`: time in the format 4:00:00 PM
    - `datetime__time_posix`: time in the format of a posix timestamp
    - `datetime__formatted`: datetime rendered in format specified by `format`

## Github
```yaml
checks:
  - github:
      source:
        type: github
        owner: haondt
        repo: pyreminder
      destinations:
        - type: console
          template: "Version ${github__tag} of pyreminder was released ${github__published_at}!"
      period: 1d
```

- config:
    - `owner`: owner of github repo to watch
    - `repo`: name of github repo to watch
- fires: when a new release is published
- variables:
    - `github__tag`: the tag of the new release
    - `github__published_at`: how long ago the release was published
    - `github__body`: the body of the release message
    - `github__url`: the url of the release page

## Apt Repository
```yaml
checks:
  - sonarr-apt:
      source:
        type: apt
        url: https://apt.sonarr.tv/debian
        component: main
        dist: jessie
        package: sonarr
      destinations:
        - type: console
          template: "Version ${apt__version} of Sonarr is available."
      period: 1d
```

- config:
    - `url`: url of repository to watch
    - `component`: component to watch
    - `dist`: dist of package to watch
    - `package`: package to watch
- fires: when a version of the package is released
- variables:
    - `apt__version`: most recently pushed version of package

## Docker Hub
```yaml
checks:
  - dockerhub:
      source:
        type: docker-hub
        namespace: haumea
        repository: pyreminder
        tag: latest
      destinations:
        - type: console
          template: "New version of ${docker_hub__image} pushed ${docker_hub__last_updated}."
      period: 1d
```

- config:
    - `namespace`: namespace of image to watch
    - `repository`: repository of image to watch
    - `tag`: tag of image to watch
- fires: when a new image is pushed
- variables:
    - `docker_hub__last_updated`: how long ago the image was updated
    - `docker_hub__image`: the name of the image
    - `docker_hub__version`: the most recent numeric (x.y.z) image that was released at the same time as the watched image (probably the update version)

