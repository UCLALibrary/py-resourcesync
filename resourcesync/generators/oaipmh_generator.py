# -*- coding: utf-8 -*-

"""
:samp:`An OAI-PMH Generator.`
"""

from resourcesync.core.generator import Generator
from hashlib import md5
from resync import Resource

from sickle import Sickle
from requests import get
from bs4 import BeautifulSoup

class OAIPMHGenerator(Generator):
    """Generator class for connecting OAI-PMH harvests to ResourceSync.

    In order to use this generator, `ResourceSync` must have been called with
    a special kwarg called `generator_params`. It is a dict with the following
    properties, all strings:

    OAIPMHEndpoint - URL fragment to which query parameters are appended
    OAIPMHMetadataPrefix - metadata prefix query param
    OAIPMHSet - set query param
    """
    # TODO: add more OAI-PMH params
    def __init__(self, params, rsxml=None):

        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):

        provider = Sickle(self.params.generator_params['OAIPMHEndpoint'])
        headers = provider.ListIdentifiers(
            metadataPrefix=self.params.generator_params['OAIPMHMetadataPrefix'],
            set=self.params.generator_params['OAIPMHSet'])

        return list(map(self.oaiToResourceSync, headers))

    def oaiToResourceSync(self, header):
        """Maps an OAI-PMH identifier to a ResourceSync Resource.

        https://github.com/resync/resync/blob/master/resync/resource.py
        """
        # TODO: logging

        soup = BeautifulSoup(header.raw.encode('utf-8'), 'xml')

        uri = '{}?verb=GetRecord&identifier={}&metadataPrefix={}'.format(
            self.params.generator_params['OAIPMHEndpoint'],
            soup.identifier.text,
            self.params.generator_params['OAIPMHMetadataPrefix'])

        r = get(uri)

        lastmod = soup.header.datestamp.text

        m = md5()
        m.update(uri.encode('utf-8'))
        m = m.hexdigest()

        length = len(r.content) # or, r.headers['Content-Length'], if available

        mime_type = r.headers['Content-Type']

        return Resource(
            uri=uri,
            lastmod=lastmod,
            md5=m,
            length=length,
            mime_type=mime_type
        )
