# -*- coding: utf-8 -*-

import unittest
from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.oaipmh_generator import OAIPMHGenerator
from requests_mock import mock
from tests.test_oaipmh_generator_mock_responses import mock_responses
import logging


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class OAIPMHGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.OAIPMHBaseURL        = "http://example.com/oai"
        self.OAIPMHSet            = "test"
        self.OAIPMHMetadataPrefix = "oai_dc"
        self.OAIPMHGeneratorParams = {
            'OAIPMHBaseURL':        self.OAIPMHBaseURL,
            'OAIPMHSet':            self.OAIPMHSet,
            'OAIPMHMetadataPrefix': self.OAIPMHMetadataPrefix
            }

        self.GetRecordURLTemplate       = "{}?verb=GetRecord&identifier={}&metadataPrefix={}"
        self.ListIdentifiersURLTemplate = "{}?verb=ListIdentifiers&set={}&metadataPrefix={}"
        self.httpResponseHeaders        = {"content-type": "text/xml"}

    def test_generate(self):

        with mock() as m:

            testNum = 0

            # create two records, A and B
            urlGetRecordA      = self.GetRecordURLTemplate.format(self.OAIPMHBaseURL, "A", self.OAIPMHMetadataPrefix)
            urlGetRecordB      = self.GetRecordURLTemplate.format(self.OAIPMHBaseURL, "B", self.OAIPMHMetadataPrefix)
            urlListIdentifiers = self.ListIdentifiersURLTemplate.format(self.OAIPMHBaseURL, self.OAIPMHSet, self.OAIPMHMetadataPrefix)

            m.get(urlGetRecordA,      text=mock_responses[testNum][urlGetRecordA],      headers=self.httpResponseHeaders)
            m.get(urlGetRecordB,      text=mock_responses[testNum][urlGetRecordB],      headers=self.httpResponseHeaders)
            m.get(urlListIdentifiers, text=mock_responses[testNum][urlListIdentifiers], headers=self.httpResponseHeaders)

            metadata = OAIPMHGenerator(params=self.OAIPMHGeneratorParams).generate()
            LOG.debug(metadata)

            # save so we can track changes to record B
            oldMetadata = metadata

            # expect two records in the metadata list
            self.assertTrue(len(metadata) == 2)
            self.assertTrue(len(list(filter(lambda x: x.uri == urlGetRecordA, metadata))) == 1)
            self.assertTrue(len(list(filter(lambda x: x.uri == urlGetRecordB, metadata))) == 1)



            testNum = 1

            # delete record A, update record B, create record C
            urlGetRecordA = self.GetRecordURLTemplate.format(self.OAIPMHBaseURL, "A", self.OAIPMHMetadataPrefix)
            urlGetRecordB = self.GetRecordURLTemplate.format(self.OAIPMHBaseURL, "B", self.OAIPMHMetadataPrefix)
            urlGetRecordC = self.GetRecordURLTemplate.format(self.OAIPMHBaseURL, "C", self.OAIPMHMetadataPrefix)
            urlListIdentifiers = self.ListIdentifiersURLTemplate.format(self.OAIPMHBaseURL, self.OAIPMHSet, self.OAIPMHMetadataPrefix)

            m.get(urlGetRecordA,      text=mock_responses[testNum][urlGetRecordA],      headers=self.httpResponseHeaders)
            m.get(urlGetRecordB,      text=mock_responses[testNum][urlGetRecordB],      headers=self.httpResponseHeaders)
            m.get(urlGetRecordC,      text=mock_responses[testNum][urlGetRecordC],      headers=self.httpResponseHeaders)
            m.get(urlListIdentifiers, text=mock_responses[testNum][urlListIdentifiers], headers=self.httpResponseHeaders)

            metadata = OAIPMHGenerator(params=self.OAIPMHGeneratorParams).generate()
            LOG.debug(metadata)

            # compare md5 values of each version of record B to check for updates
            oldMD5 = list(filter(lambda x: x.uri == urlGetRecordB, oldMetadata))[0].md5
            newMD5 = list(filter(lambda x: x.uri == urlGetRecordB, metadata))[0].md5
            updatedRecordB = oldMD5 != newMD5

            # expect two records in the metadata list
            # record A was deleted, record B was updated, record C was created
            self.assertTrue(len(metadata) == 2)
            self.assertTrue(len(list(filter(lambda x: x.uri == urlGetRecordA, metadata))) == 0)
            self.assertTrue(len(list(filter(lambda x: x.uri == urlGetRecordB, metadata))) == 1 and updatedRecordB)
            self.assertTrue(len(list(filter(lambda x: x.uri == urlGetRecordC, metadata))) == 1)

if __name__ == "__main__":
    unittest.main()
