import json
import pkgutil


class UserAgent(object):
    default_agents = json.loads(pkgutil.get_data(__name__, "default_agents.txt"))

    def __init__(self, agents=None):
        self.agents = agents

        if not self.agents:
            self.agents = UserAgent.default_agents

    @classmethod
    def common(cls, amount=20):
        return cls(agents=UserAgent.default_agents[:amount])

    @property
    def default(self):
        return self.default_agents[0]['useragent']

    def random(self):
        import random
        agent = random.choice(self.agents)

        if isinstance(agent, dict) and agent.get('useragent'):
            return agent['useragent']
        # Continue error check if needed
        return agent
