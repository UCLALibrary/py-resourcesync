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

    The following parameters are required for its use:

    OAIPMHEndpoint - URL fragment to which query parameters are appended
    OAIPMHMetadataPrefix - metadata prefix query param
    OAIPMHSet - set query param
    """
    # TODO: add more OAI-PMH params
    def __init__(self, params, rsxml=None):

        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):

        provider = Sickle(self.params.OAIPMHEndpoint)
        headers = provider.ListIdentifiers(
            metadataPrefix=self.params.OAIPMHMetadataPrefix,
            set=self.params.OAIPMHSet)

        return list(map(self.oaiToResourceSync, headers))

    def oaiToResourceSync(self, header):
        """Maps an OAI-PMH identifier to a ResourceSync Resource.

        https://github.com/resync/resync/blob/master/resync/resource.py
        """
        # TODO: logging

        soup = BeautifulSoup(header.raw.encode('utf-8'), 'xml')

        uri = '{}?verb=GetRecord&identifier={}&metadataPrefix={}'.format(
            self.params.OAIPMHEndpoint,
            soup.identifier.text,
            self.params.OAIPMHMetadataPrefix)

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
