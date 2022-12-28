import re, os, yaml, requests, json, string, pytz, hashlib, dateutil.parser, sched, time
from datetime import datetime, timedelta
from babel.dates import format_timedelta, format_time, format_datetime, get_timezone
from babel.dates import UTC as tz_UTC


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

        self.enrichments = []
        if 'enrichments' in data:
            self.enrichments = [sourceFactory.Create(s) for s in data['enrichments']]

        self.source = sourceFactory.Create(data['source'])
        self.destinations = [destinationFactory.Create(d) for d in data['destinations']]

        time_re = re.compile(r"^(?:(?P<d>[0-9]+)d)?(?:(?P<h>[0-9]+)h)?(?:(?P<m>[0-9]+)m)?(?:(?P<s>[0-9]+)s)?$")
        gd = time_re.match(data['period']).groupdict()
        self.period = timedelta(
            days=int(gd['d'] or 0),
            hours=int(gd['h'] or 0),
            minutes=int(gd['m'] or 0),
            seconds=int(gd['s'] or 0)
        )

    def _enrich(self, data):
        for k in self.meta:
            data["meta__" + k] = self.meta[k]
        for e in self.enrichments:
            data = e.enrich(data)
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
        elif sourceType == 'reminder':
            return Reminder_Source(self.state_manager, config)
        elif sourceType == 'datetime':
            return DateTime_Source(self.state_manager, config)
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
        return Template(template_name)

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
class DateTime_Source:
    def __init__(self, state_manager, config):
        self.tz = tz_UTC
        if 'tz' in config:
            self.tz = get_timezone(config['tz'])

        self.format = None
        if 'format' in config:
            self.format = config['format']
    def enrich(self, data):
        now = datetime.utcnow()
        data['datetime__date_short'] = format_datetime(now, format='yyyy/MM/dd', tzinfo=self.tz, locale='en')
        data['datetime__date_long'] = format_datetime(now, format='MMMM d, yyyy', tzinfo=self.tz, locale='en')
        data['datetime__date_full'] = format_datetime(now, format='EEEE, MMMM d, yyyy', tzinfo=self.tz, locale='en')
        data['datetime__time_short'] = format_time(now, format='h:mm a', tzinfo=self.tz, locale='en')
        data['datetime__time_long'] = format_time(now, format='h:mm:SS a', tzinfo=self.tz, locale='en')
        data['datetime__posix'] = now.timestamp()
        if self.format is not None:
            data['datetime__formatted'] = format_datetime(now, format=self.format, tzinfo=self.tz, locale='en')
        return data
    def check(self, force=False):
        return (False, None)

class Reminder_Source:
    def __init__(self, state_manager, config):
        pass
    def enrich(self, data):
        return data
    def check(self, force=False):
        return (True, {})

class GitHub_Source:
    def __init__(self, state_manager, config):
        self.state_manager = state_manager
        self.owner = config['owner']
        self.repo = config['repo']

        self.state_key = f"github:({self.owner},{self.repo}))"

    def enrich(self, data):
        _, e = self.check(True)
        for k in e:
            data[k] = e[k]
        return data

    def check(self, force=False):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        j = json.loads(requests.get(url).content)

        for k in ["tag_name", "published_at"]:
            if k not in j:
                raise Exception(f"missing key {k} in response from url {url}")

        tag = j["tag_name"]
        published_at = j["published_at"]
        key = (tag, published_at)
        hsh = int(hashlib.md5(str(key).encode('utf-8')).hexdigest(), 16)

        data =  {
            "github__tag": tag,
            "github__published_at": format_timedelta(dateutil.parser.isoparse(published_at) - datetime.now(pytz.utc), add_direction=True),
            "github__body": j["body"],
            "github__url": f"https://github.com/{self.owner}/{self.repo}/releases/tag/{tag}"
        }

        if force:
            return (True, data)

        oldState = self.state_manager.getState(self.state_key)
        if oldState is not None:
            if oldState['hash'] == hsh:
                return (False, None)

        newState = {
            "hash": hsh
        }
        self.state_manager.setState(self.state_key, newState)
        return (True, data)

class DockerHub_Source:
    def __init__(self, state_manager, config):
        self.state_manager = state_manager
        self.namespace = 'library'
        if 'namespace' in config:
            self.namespace = config['namespace']
        self.repo = config['repository']
        self.tag = config['tag']

        self.state_key = f"docker-hub:({self.namespace},{self.repo},{self.tag})"

    def enrich(self, data):
        _, e = self.check(True)
        for k in e:
            data[k] = e[k]
        return data

    def check(self, force=False):
        url = f"https://hub.docker.com/v2/namespaces/{self.namespace}/repositories/{self.repo}/tags/{self.tag}"
        j = json.loads(requests.get(url).content)

        for k in ["tag_last_pushed"]:
            if k not in j:
                raise Exception(f"missing key {k} in response from url {url}")

        last_updated = j["tag_last_pushed"]
        key = (last_updated)
        hsh = int(hashlib.md5(str(key).encode('utf-8')).hexdigest(), 16)
        last_updated_datetime = dateutil.parser.isoparse(last_updated)

        image = f"{self.namespace}/{self.repo}:{self.tag}"
        if self.namespace == 'library': # docker official image
            image = f"{self.repo}:{self.tag}"
        data =  {
            "docker_hub__last_updated": format_timedelta(last_updated_datetime - datetime.now(pytz.utc), add_direction=True),
            "docker_hub__image": image,
            "docker_hub__version": self.tag
        }

        trigger = True

        if not force:
            oldState = self.state_manager.getState(self.state_key)
            if oldState is not None:
                if oldState['hash'] == hsh:
                    trigger = False
            if trigger:
                newState = { "hash": hsh }
                self.state_manager.setState(self.state_key, newState)

        if trigger:
            tags_url = f"https://hub.docker.com/v2/namespaces/{self.namespace}/repositories/{self.repo}/tags?page_size=20"
            j = json.loads(requests.get(tags_url).content)
            version_re = re.compile(r"^((?:[0-9]+\.?)+)$")
            for res in j['results']:
                ts = dateutil.parser.isoparse(res['tag_last_pushed'])
                if abs((ts - last_updated_datetime).total_seconds()) > 10:
                    if version_re.match(res['name']):
                        data['docker_hub__version']  = res['name']
                        break

        return (trigger, data)

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
        message = {
            "embeds": [
                {
                    "type": "rich",
                    "description": self.template.render(data)
                }
            ]
        }
        requests.post(self.url, json=message)

# main worker
class Scheduler:
    def __init__(self, data_dir, config):
        stateManager = StateManager(data_dir)
        sourceFactory = SourceFactory(stateManager)
        templateManager = TemplateManager(config['templates'] if 'templates' in config else [])
        destinationFactory = DestinationFactory(templateManager)
        checkFactory = CheckFactory(sourceFactory, destinationFactory)

        self.checks = []
        for check in config['checks']:
            check_name = next(iter(check))
            self.checks.append(checkFactory.Create(check_name, check[check_name] ))

        self.scheduler = sched.scheduler(time.time, time.sleep)

        for check in self.checks:
            self.runCheckAndReschedule(check)

    def runCheckAndReschedule(self, check):
        check.check()
        self.scheduler.enter(check.period.total_seconds(), 1, self.runCheckAndReschedule, (check,))

    def run(self):
        self.scheduler.run()

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.env_var_re = re.compile(r"\$\{([^}^{]+)\}")

    def path_constructor(self, loader, node):
        value = node.value
        match = self.env_var_re.match(value)
        env_var = match.group()[2:-1]
        if os.environ.get(env_var) is None:
            raise Exception(f"Missing environment variable \"{env_var}\"")
        return os.environ.get(env_var) + value[match.end():]

    def loadConfig(self):
        yaml.add_implicit_resolver('!path', self.env_var_re)
        yaml.add_constructor('!path', lambda l, n: self.path_constructor(l, n))

        app_config = None
        with open(self.config_file) as f:
            s = f.read()
            app_config = yaml.load(s, Loader=yaml.FullLoader)

        return app_config



# do work
data_dir = "/data"
config_file = "/config/pyreminder.yml"

configLoader = ConfigLoader(config_file)
scheduler = Scheduler(data_dir, configLoader.loadConfig())

scheduler.run()