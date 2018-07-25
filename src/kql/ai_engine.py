import os.path
import re
from kql.ai_client import AppinsightsClient
import requests
import getpass

class AppinsightsEngine(object):
    schema = 'appinsights://'

    @classmethod
    def tell_format(cls):
        return """
               appinsights://appid('appid').appkey('appkey')

               ## Note: if appkey is missing, user will be prompted to enter appkey"""

    # Object constructor
    def __init__(self, conn_str, current=None):
        self.api_version = 'v1'
        self.name = None
        self.bind_url = None
        self.client = None
        self.cluster_url = 'https://api.applicationinsights.io/{0}/apps'.format(self.api_version)
        self.parse_connection_str(conn_str, current)


    def __eq__(self, other):
        return self.bind_url and self.bind_url == other.bind_url

    def parse_connection_str(self, conn_str : str, current):
        self.username = None
        self.password = None
        self.appid = None
        self.appkey = None
        self.bind_url = None
        self.name = None
        match = None
        # conn_str = "kusto://username('michabin@microsoft.com').password('g=Hh-h34G').cluster('Oiildc').database('OperationInsights_PFS_PROD')"
        if not match:
            pattern = re.compile(r'^appinsights://appid\((?P<appid>.*)\)\.appkey\((?P<appkey>.*)\)$')
            match = pattern.search(conn_str)
            if match:
                self.appid = match.group('appid').strip()[1:-1]
                self.appkey = match.group('appkey').strip()[1:-1]
                self.cluster_name = 'appinsights'
                self.database_name = self.appid
                if self.appkey.lower() == '<appkey>':
                    self.appkey = getpass.getpass(prompt = 'please enter appkey: ')

        if not match:
            pattern = re.compile(r'^appinsights://appid\((?P<appid>.*)\)$')
            match = pattern.search(conn_str)
            if match:
                self.appid = match.group('appid').strip()[1:-1]
                self.cluster_name = 'appinsights'
                self.database_name = self.appid
                self.appkey = getpass.getpass(prompt = 'please enter appkey: ')

        if not match:
            raise AppinsightsEngineError('Invalid connection string.')

        if self.database_name:
            self.bind_url = "appinsights://appid('{0}').appkey('{1}').cluster('{2}').database('{3}')".format(self.appid,self.appkey,self.cluster_name,self.database_name)
            self.name = '{0}@appinsights'.format(self.appid)


    def get_client(self):
        if not self.client:
            if not self.appid or not self.appkey:
                raise AppinsightsEngineError("appid and appkey are not defined.")
            self.client = AppinsightsClient(appid=self.appid, appkey=self.appkey, version=self.api_version)
        return self.client

    def get_database(self):
        database_name = self.database_name
        if not self.database_name:
            raise AppinsightsEngineError("Database is not defined.")
        return database_name


class AppinsightsEngineError(Exception):
    """Generic error class."""
