class UserAgent(object):
    default_agents = [
        {
            "percent": "18.2%",
            "system": "Chrome 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "11.5%",
            "system": "Firefox 95.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "6.4%",
            "system": "Chrome 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "4.4%",
            "system": "Chrome 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        },
        {
            "percent": "3.8%",
            "system": "Firefox 95.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "3.6%",
            "system": "Firefox 91.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
        },
        {
            "percent": "3.2%",
            "system": "Firefox 95.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "2.7%",
            "system": "Firefox 95.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "2.4%",
            "system": "Chrome 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        },
        {
            "percent": "2.1%",
            "system": "Edge 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"
        },
        {
            "percent": "2.1%",
            "system": "Safari 15.1 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
        },
        {
            "percent": "2.0%",
            "system": "Safari 15.2 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15"
        },
        {
            "percent": "1.7%",
            "system": "Chrome 96.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "1.6%",
            "system": "Chrome 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        },
        {
            "percent": "1.5%",
            "system": "Chrome 97.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        },
        {
            "percent": "1.0%",
            "system": "Firefox 94.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
        },
        {
            "percent": "1.0%",
            "system": "Chrome 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
        },
        {
            "percent": "0.7%",
            "system": "Chrome 96.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        },
        {
            "percent": "0.7%",
            "system": "Chrome 96.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        },
        {
            "percent": "0.6%",
            "system": "Safari 14.1 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
        },
        {
            "percent": "0.6%",
            "system": "Firefox 95.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "0.5%",
            "system": "Chrome 96.0 Win7",
            "useragent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "0.5%",
            "system": "Firefox 91.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        },
        {
            "percent": "0.5%",
            "system": "Firefox 78.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
        },
        {
            "percent": "0.5%",
            "system": "Edge 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53"
        },
        {
            "percent": "0.4%",
            "system": "Firefox 91.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        },
        {
            "percent": "0.4%",
            "system": "Firefox 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
        },
        {
            "percent": "0.4%",
            "system": "Firefox 95.0 Win7",
            "useragent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "0.4%",
            "system": "Edge 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"
        },
        {
            "percent": "0.4%",
            "system": "Safari 15.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
        },
        {
            "percent": "0.4%",
            "system": "Firefox 94.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
        },
        {
            "percent": "0.4%",
            "system": "Chrome 95.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        },
        {
            "percent": "0.4%",
            "system": "Opera 82 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 OPR/82.0.4227.33"
        },
        {
            "percent": "0.4%",
            "system": "Firefox 94.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
        },
        {
            "percent": "0.3%",
            "system": "Firefox 94.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0"
        },
        {
            "percent": "0.3%",
            "system": "Chrome 95.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        },
        {
            "percent": "0.3%",
            "system": "Edge 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43"
        },
        {
            "percent": "0.3%",
            "system": "Opera 82 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43"
        },
        {
            "percent": "0.3%",
            "system": "Chrome 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        },
        {
            "percent": "0.3%",
            "system": "Chrome 97.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        },
        {
            "percent": "0.3%",
            "system": "Chrome 96.0 Win8.1",
            "useragent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "0.3%",
            "system": "Firefox 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0"
        },
        {
            "percent": "0.3%",
            "system": "Chrome 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "0.3%",
            "system": "Safari 15.1 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
        },
        {
            "percent": "0.2%",
            "system": "Opera 82 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50"
        },
        {
            "percent": "0.2%",
            "system": "Chrome 96.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "0.2%",
            "system": "Opera 82 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 OPR/82.0.4227.23"
        },
        {
            "percent": "0.2%",
            "system": "Chrome 96.0 Win7",
            "useragent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        },
        {
            "percent": "0.2%",
            "system": "Firefox 78.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
        },
        {
            "percent": "0.2%",
            "system": "Firefox 95.0 Win8.1",
            "useragent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
        },
        {
            "percent": "0.2%",
            "system": "DefaultProperties unknown",
            "useragent": "null"
        },
        {
            "percent": "0.2%",
            "system": "Chrome 99.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36"
        },
        {
            "percent": "0.2%",
            "system": "Chrome 95.0 Linux",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        },
        {
            "percent": "0.2%",
            "system": "Safari 13.1 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"
        },
        {
            "percent": "0.2%",
            "system": "Edge 97.0 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55"
        },
        {
            "percent": "0.2%",
            "system": "Chrome 96.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        },
        {
            "percent": "0.2%",
            "system": "Safari 14.0 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
        },
        {
            "percent": "0.2%",
            "system": "Safari 14.1 macOS",
            "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        },
        {
            "percent": "0.2%",
            "system": "Opera 81 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61"
        },
        {
            "percent": "0.2%",
            "system": "Opera 81 Win10",
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61"
        }
    ]

    def __init__(self, agents=None):
        self.agents = agents

        if self.agents is None:
            self.agents = self.default_agents

    @classmethod
    def common(cls, amount=20):
        return cls(agents=UserAgent.default_agents[:amount])

    def random(self):
        import random
        agent = random.choice(self.agents)

        if isinstance(agent, dict) and agent.get('useragent'):
            return agent['useragent']
        # Continue error check if needed
        return agent
