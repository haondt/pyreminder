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
| `tag` | the associated tag |
| `published_at` | how long ago the release was published|
| `body` | the body of the release message |
| `url` | the url of the release page |

docker-hub source:
| | |
|---|---|
| `last_updated` | how long ago the release was updated |
| `image` | name of the docker image |
| `version` | the most recent numeric image that was released at the same time as the source release (probably the updated version) |