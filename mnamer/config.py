import json
from collections import MutableMapping
from os import environ
from string import Template

from mnamer import *


class Config(MutableMapping):
    """ Stores mnamer's configuration. Config objects can be interacted with
    like a regular dict. Keys are case insensitive, but however trivial
    validation is used against key name and value types.
    """

    DEFAULTS = {

        # General Options
        'batch': False,
        'dots': False,
        'extension_mask': [
            'avi',
            'm4v',
            'mp4',
            'mkv',
            'ts',
            'wmv',
        ],
        'lower': False,
        'max_hits': 15,
        'recurse': False,
        'verbose': False,

        # Movie related
        'movie_api': 'tmdb',
        'movie_destination': '',
        'movie_template': (
            '<$title >'
            '<($year)>/'
            '<$title >'
            '<($year)>'
            '<$extension>'
        ),

        # Television related
        'television_api': 'tvdb',
        'television_destination': '',
        'television_template': (
            '<$series/>'
            '<$series - >'
            '< - S$season>'
            '<E$episode - >'
            '< - $title>'
            '<$extension>'
        ),

        # API Keys -- consider using your own or IMDb if limits are hit
        'api_key_tmdb': 'db972a607f2760bb19ff8bb34074b4c7',
        'api_key_tvdb': 'E69C7A2CEF2F3152'

    }

    def __init__(self, **params):
        self._dict = dict()

        # Config load order: defaults, config file, parameters
        self._dict.update(self.DEFAULTS)  # Skips setitem validations
        for path in ('.mnamer.json', config_path):
            try:
                self.deserialize(path)
            except IOError:
                pass
        self.update(params)  # Follows setitem validations

    def __len__(self):
        return self._dict.__len__()

    def __iter__(self):
        return self._dict.__iter__()

    def __getitem__(self, key: str):
        return self._dict.__getitem__(key.lower())

    def __delitem__(self, key: str):
        raise NotImplementedError('values can be modified but keys cannot')

    def __setitem__(self, key: str, value: str):
        if key == 'television_api' and value not in ['tvdb']:
            raise ValueError()
        elif key == 'movie_api' and value not in ['imdb', 'tmdb']:
            raise ValueError()
        elif key not in self.DEFAULTS:
            raise KeyError(f'attempted to set invalid key ({key})')
        elif not isinstance(value, type(self._dict[key])):
            raise TypeError(f'attempted to set invalid type ({key})')
        else:
            self._dict[key] = value

    def deserialize(self, path: str):
        """ Reads JSON file and overlays parsed values over current configs
        """
        t = Template(path).substitute(environ)
        with open(file=t, mode='r') as fp:
            self.update(json.load(fp))

    def serialize(self, path: str):
        """ Serializes Config object as a JSON file
        """
        t = Template(path).substitute(environ)
        with open(file=t, mode='w') as fp:
            json.dump(dict(self), fp, indent=4)
