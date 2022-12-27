# templates

Templates are rendered using python [template strings](https://docs.python.org/3/library/string.html#template-strings). The available keys will depend on the source.

All sources:
| | |
|---|---|
| `check__name` | the name of the check |
| `meta__<any>` | Any keys in the `meta` field will be available as `meta__YOURKEY` |


github source:
| | |
|---|---|
| `github__tag` | the associated tag |
| `github__published_at` | how long ago the release was published|
| `github__body` | the body of the release message |
| `github__url` | the url of the release page |

docker-hub source:
| | |
|---|---|
| `docker_hub__last_updated` | how long ago the release was updated |
| `docker_hub__image` | name of the docker image |
| `docker_hub__version` | the most recent numeric image that was released at the same time as the source release (probably the updated version) |

plex source:
| | |
|---|---|
| `plex__url` | url to download plex media server |
\* plex source doesn't check anything. It's just there for enrichment, to make grabbing the link easier.