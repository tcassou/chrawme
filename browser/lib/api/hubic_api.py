# -*- coding: utf-8 -*-

import cStringIO
import os
import requests
import yaml

from browser.lib.api.base_api import BaseAPI

CREDENTIAL_FILE = os.path.dirname(__file__) + '/credentials.yml'


class HubicAPI(BaseAPI):
    """Provide a HubiC authentication interface.

    References:
        - https://hubic.com/en/
        - https://api.hubic.com/

    This class assumes that you already have
        - an app declared and allowed on your Hubic account
        - a refresh token to query the Hubic API

    Read the above references to set it up.
    """

    class Meta:
        name = 'hubic'
        remote = True

    @classmethod
    def list_content(cls, path):
        """List directory contents needed to enumerate files and folders.

        :param str path: path to directory

        :return: folder content
        :rtype: [object]
        """
        return requests.get('/'.join([cls.get_endpoint(), cls.main_container()]), headers=cls.headers()).json()

    @classmethod
    def list_folders(cls, path, content):
        """List folders under path.

        :param str path: current path
        :param [object] content: current folder contents

        :return: None
        :rtype: NoneType
        """
        cls.folders = [
            {
                'label': el['name'].replace(path + '/', ''),
                'value': el['name'],
                'last_modified': el['last_modified'],
            }
            for el in content if cls.is_path_folder(el, path)
        ]

    @classmethod
    def list_images(cls, path, content):
        """List images under path.

        :param str path: current path
        :param [object] content: current folder contents

        :return: None
        :rtype: NoneType
        """
        cls.images = [
            cls.create_image(i, path, el['name'].replace(path + '/', ''), process=False)
            for i, el in enumerate([el for el in content if cls.is_path_image(el, path)])
        ]

    @classmethod
    def list_autocomplete_source(cls, path, content):
        """Find the directory tree structure excluding files, to use in the autocomplete feature.

        :param str path: directory to scan
        :param [object] content: current folder contents

        :return: list of directories
        :rtype: [str]
        """
        cls.autocomplete_source = [el['name'] for el in content if cls.is_dir(el) and cls.is_under_path(el, path)]

    @classmethod
    def is_dir(cls, entry):
        """Check if entry points to a directory.

        :param {str: object} entry: json entry in Hubic

        :return: True if directory
        :rtype: bool
        """
        return entry['content_type'] == 'application/directory'

    @classmethod
    def is_image(cls, entry):
        """Check if entry points to an image.

        :param {str: object} entry: json entry in Hubic

        :return: True if image
        :rtype: bool
        """
        return 'image/' in entry['content_type']

    @classmethod
    def is_path_folder(cls, entry, path):
        """Check if directory entry belongs to path.

        :param {str: object} entry: json entry in Hubic
        :param str path: current path

        :return: True if belongs to path
        :rtype: bool
        """
        if entry['name'] == path or entry['name'].startswith('.'):
            return False
        if not cls.is_dir(entry) or not cls.is_under_path(entry, path):
            return False

        return '/' not in entry['name'].replace('' if path == '' else path + '/', '')

    @classmethod
    def is_path_image(cls, entry, path):
        """Check if image entry belongs to path.

        :param {str: object} entry: json entry in Hubic
        :param str path: current path

        :return: True if belongs to path
        :rtype: bool
        """
        if entry['name'].startswith('.') or not cls.is_image(entry):
            return False

        return '/' not in entry['name'].replace('' if path == '' else path + '/', '')

    @classmethod
    def is_under_path(cls, entry, path):
        """Check if entry is located under path.

        :param {str: object} entry: json entry in Hubic
        :param str path: current path

        :return: True if under path
        :rtype: bool
        """
        return entry['name'].startswith(path)

    @classmethod
    def main_container(cls):
        """Find the main Hubic container, defined as the one containing the biggest number of objects.

        :return: container name
        :rtype: str
        """
        if cls.container is None:
            containers = requests.get(cls.get_endpoint(), headers=cls.headers()).json()
            cls.container = max(containers, key=lambda x: x['count'])['name']
        return cls.container

    @classmethod
    def headers(cls):
        """Get the authentication header.

        :returns: The headers used for authenticating requests.
        :rtype: dict
        """
        if cls.auth_token is None:
            cls.fetch_credentials(session)

        return {
            'X-Auth-Token': cls.auth_token,
            "Accept": "application/json",
        }

    @classmethod
    def refresh_access_token(cls):
        """Request an access token from the HubiC API.

        :return: None
        :rtype: NoneType
        """
        data = {
            "refresh_token": cls.refresh_token,
            "grant_type": "refresh_token",
        }
        r = requests.post(
            "https://api.hubic.com/oauth/token", data=data, auth=requests.auth.HTTPBasicAuth(cls.client_id, cls.secret))
        cls.access_token = r.json()['access_token']

    @classmethod
    def get_endpoint(cls):
        """Get the HubiC storage endpoint uri.

        :returns: The uri to use for object-storage v1 requests.
        :rtype: string
        """
        if cls.endpoint is None:
            cls.fetch_credentials()
        return cls.endpoint

    @classmethod
    def fetch_credentials(cls):
        """Fetch the endpoint URI and authorization token for this session.

        :return: None
        :rtype: NoneType
        """
        cls.refresh_access_token()
        headers = {"Authorization": "Bearer {}".format(cls.access_token)}
        credentials = requests.get("https://api.hubic.com/1.0/account/credentials", headers=headers).json()
        cls.endpoint = credentials['endpoint']
        cls.auth_token = credentials['token']

    @classmethod
    def load(cls):
        """Load Hubic API credentials.

        :return: None
        :rtype: NoneType
        """
        # Crendentials
        with open(CREDENTIAL_FILE, 'r') as local_stream:
            credentials = yaml.load(local_stream)['hubic']
        cls.client_id = credentials['client_id']
        cls.secret = credentials['secret']
        cls.refresh_token = credentials['refresh_token']
        # Useful class variables
        cls.access_token  = None
        cls.endpoint = None
        cls.auth_token = None
        cls.container = None

    @classmethod
    def file_stream(cls):
        """Define the file input stream to read the image from Hubic.

        :return: method to read the file
        :rtype: method
        """
        def read_file(filename):
            """Read the image file from Hubic.

            :param str filename: name of the image

            :return: file buffer
            :rtype: cStringIO.StringIO
            """
            resp = requests.get('/'.join([cls.get_endpoint(), cls.main_container(), filename]), headers=cls.headers())
            return cStringIO.StringIO(resp.content)

        return read_file


HubicAPI.load()
