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
    """Generator class for using ResourceSync with OAI-PMH records.

    In order to use this generator, the following additional key word
    arguments must be passed to the ResourceSync class constructor:

    OAIPMHBaseURL           the base URL for OAI-PMH requests, to which
        query parameters are appended to form the full request URL
    OAIPMHMetadataPrefix    the metadata prefix argument, as defined in
        https://www.openarchives.org/OAI/openarchivesprotocol.html#MetadataNamespaces
    OAIPMHSet               the set argument, as defined in
        https://www.openarchives.org/OAI/openarchivesprotocol.html#Set
    """
    def __init__(self, params=None, rsxml=None):

        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):
        """Returns a list of ResourceSync resources that each represent one
        full OAI-PMH record (i.e., the result of a GetRecord request).
        """

        provider = Sickle(self.params['OAIPMHBaseURL'])

        # TODO: add more OAI-PMH params
        headers = provider.ListIdentifiers(ignore_deleted=True,
            metadataPrefix=self.params['OAIPMHMetadataPrefix'],
            set=self.params['OAIPMHSet'])

        return list(map(self.oaiToResourceSync, headers))

    def oaiToResourceSync(self, header):
        """Maps an OAI-PMH record identifier to a ResourceSync Resource."""
        # TODO: logging

        soup = BeautifulSoup(header.raw.encode('utf-8'), 'xml')

        uri = '{}?verb=GetRecord&identifier={}&metadataPrefix={}'.format(
            self.params['OAIPMHBaseURL'],
            soup.identifier.text,
            self.params['OAIPMHMetadataPrefix'])

        # do a GET request for each record
        r = get(uri)

        lastmod = soup.header.datestamp.text
        body = str(BeautifulSoup(r.content, 'xml').GetRecord).encode('utf-8')

        # compute MD5 of the body
        m = md5()
        m.update(body)
        m = m.hexdigest()

        length = len(body)

        mime_type = r.headers['Content-Type']

        return Resource(
            uri=uri,
            lastmod=lastmod,
            md5=m,
            length=length,
            mime_type=mime_type
        )
