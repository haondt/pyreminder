import re, os, yaml, requests, json, string, pytz, hashlib
from datetime import datetime
from babel.dates import format_timedelta



# check
class Check:
    def __init__(self, name, data, sourceFactory, destinationFactory):
        self.name = name
        self.meta = {}
        if 'meta' in data:
            self.meta = data['meta']

        self.debug = False
        if 'debug' in data:
            self.debug = data['debug']

        self.source = sourceFactory.Create(data['source'])
        self.destinations = [destinationFactory.Create(d) for d in data['destinations']]

    def _enrich(self, data):
        for k in self.meta:
            data["meta__" + k] = self.meta[k]
        data['check__name'] = self.name
        return data

    def check(self):
        result, data = self.source.check(self.debug)
        if result:
            data = self._enrich(data)
            for destination in self.destinations:
                destination.send(data)

# factories
class CheckFactory:
    def __init__(self, sourceFactory, destinationFactory):
        self.sourceFactory = sourceFactory
        self.destinationFactory = destinationFactory

    def Create(self, check_name, data):
        return Check(check_name, data, self.sourceFactory, self.destinationFactory)

class SourceFactory:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def Create(self, config):
        sourceType = config['type']
        if sourceType == 'github':
            return GitHub_Source(self.state_manager, config)
        elif sourceType == 'docker-hub':
            return DockerHub_Source(self.state_manager, config)
        else:
            raise Exception(f"No such source: {sourceType}")

class DestinationFactory:
    def __init__(self, template_manager):
        self.template_manager = template_manager

    def Create(self, config):
        config = config or {}
        destinationType = config['type']
        if destinationType == 'console':
            return Console_Destination(self.template_manager, config)
        elif destinationType == 'discord':
            return Discord_Destination(self.template_manager, config)
        else:
            raise Exception(f"No such destination: {destinationType}")

# templates
class Template:
    def __init__(self, template_string):
        self.template = string.Template((template_string))

    def render(self, data):
        return self.template.safe_substitute(data)

class StringTemplate:
    def render(self, data):
        s = None
        try:
            s = json.dumps(data)
            if s == None or len(s) == 0:
                s = str(data)
        except:
            s = str(data)
        return s

# managers
class TemplateManager:
    def __init__(self, templates):
        self.templates = {}
        for k in templates:
            self.templates[k] = Template(templates[k])

    def getTemplate(self, template_name):
        if template_name in self.templates:
            return self.templates[template_name]
        raise Exception(f"No such template: {template_name}")

class StateManager:
    def __init__(self, d):
        self.file = d + "/state.json"
        if not os.path.exists(self.file):
            self._setState({})

    def _getState(self):
        j = None
        with open(self.file) as f:
            j = json.loads(f.read())
        return j

    def _setState(self, state):
        with open(self.file, 'w+') as f:
            f.write(json.dumps(state))

    def getState(self, key):
        j = self._getState()
        if key in j:
            return j[key]
        return None

    def setState(self, key, state):
        j = self._getState()
        j[key] = state
        self._setState(j)

# sources
class GitHub_Source:
    def __init__(self, state_manager, config):
        self.state_manager = state_manager
        self.owner = config['owner']
        self.repo = config['repo']

        self.state_key = f"github:({self.owner},{self.repo}))"

    def check(self, debug):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        j = json.loads(requests.get(url).content)
        tag = j["tag_name"]
        published_at = j["published_at"]
        key = (tag, published_at)
        hsh = int(hashlib.md5(str(key).encode('utf-8')).hexdigest(), 16)

        if debug:
            return (True, {
                "tag": tag,
                "published_at": format_timedelta(datetime.fromisoformat(published_at) - datetime.now(pytz.utc), add_direction=True),
                "body": j["body"]
            })

        oldState = self.state_manager.getState(self.state_key)
        if oldState is not None:
            if oldState['hash'] == hsh:
                return (False, None)

        newState = {
            "hash": hsh
        }
        self.state_manager.setState(self.state_key, newState)
        return (True, {
            "tag": tag,
            "published_at": format_timedelta(datetime.fromisoformat(published_at) - datetime.now(pytz.utc), add_direction=True),
            "body": j["body"]
        })

class DockerHub_Source:
    def __init__(self, state_manager, config):
        self.state_manager = state_manager
        self.namespace = config['namespace']
        self.repo = config['repository']
        self.tag = config['tag']

        self.state_key = f"docker-hub:({self.namespace},{self.repo},{self.tag})"

    def check(self, debug=False):
        url = f"https://hub.docker.com/v2/namespaces/{self.namespace}/repositories/{self.repo}/tags/{self.tag}"
        j = json.loads(requests.get(url).content)
        last_updated = j["last_updated"]
        key = (last_updated)
        hsh = int(hashlib.md5(str(key).encode('utf-8')).hexdigest(), 16)

        if debug:
            return (True, {
                "last_updated": format_timedelta(datetime.fromisoformat(last_updated) - datetime.now(pytz.utc), add_direction=True),
            })

        oldState = self.state_manager.getState(self.state_key)
        if oldState is not None:
            if oldState['hash'] == hsh:
                return (False, None)

        newState = {
            "hash": hsh
        }
        self.state_manager.setState(self.state_key, newState)
        return (True, {
            "last_updated": format_timedelta(datetime.fromisoformat(last_updated) - datetime.now(pytz.utc), add_direction=True),
        })



# destinations
class Console_Destination:
    def __init__(self, template_manager, config):
        self.template = StringTemplate()
        if "template" in config:
            self.template = template_manager.getTemplate(config['template'])

    def send(self, data):
        print(f"{data['check__name']}: {self.template.render(data)}")

class Discord_Destination:
    def __init__(self, template_manager, config):
        self.url = config['webhookURL']
        self.template = StringTemplate()
        if "template" in config:
            self.template = template_manager.getTemplate(config['template'])

    def send(self, data):
        message = { "content": self.template.render(data)}
        requests.post(self.url, json=message)

# main worker
class Main:
    def __init__(self, data_dir, config):
        stateManager = StateManager(data_dir)
        sourceFactory = SourceFactory(stateManager)
        templateManager = TemplateManager(config['templates'])
        destinationFactory = DestinationFactory(templateManager)
        checkFactory = CheckFactory(sourceFactory, destinationFactory)

        self.checks = []
        for check in config['checks']:
            check_name = next(iter(check))
            self.checks.append(checkFactory.Create(check_name, check[check_name] ))

    def run(self):
        for check in self.checks:
            check.check()


# do work
config_file = "/config/pyreminder.yml"
data_dir = "/data"

time_re = re.compile(r"^(?:(?P<d>[0-9]+)d)?(?:(?P<h>[0-9]+)h)?(?:(?P<m>[0-9]+)m)?(?:(?P<s>[0-9]+)s)?$")
env_var_re = re.compile(r"\$\{([^}^{]+)\}")

def path_constructor(loader, node):
    value = node.value
    match = env_var_re.match(value)
    env_var = match.group()[2:-1]
    if os.environ.get(env_var) is None:
        raise Exception(f"Missing environment variable \"{env_var}\"")
    return os.environ.get(env_var) + value[match.end():]

yaml.add_implicit_resolver('!path', env_var_re)
yaml.add_constructor('!path', path_constructor)

app_config = None
with open(config_file) as f:
    s = f.read()
    app_config = yaml.load(s, Loader=yaml.FullLoader)

main = Main(data_dir, app_config)
main.run()