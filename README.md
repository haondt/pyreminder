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

docker-hub source:
| | |
|---|---|
| `last_updated` | how long ago the release was updated |