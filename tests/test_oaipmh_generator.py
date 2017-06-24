# -*- coding: utf-8 -*-

from resourcesync.resourcesync import ResourceSync
import unittest
import logging


#LOG = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)


class OAIPMHGeneratorTest(unittest.TestCase):

    def test_resourcesync_with_oaipmh_generator(self):
        rs = ResourceSync(
            strategy=0,
            generator="OAIPMHGenerator",
            OAIPMHEndpoint="http://digital2.library.ucla.edu/oai2_0.do",
            OAIPMHSet="apam",
            OAIPMHMetadataPrefix="oai_dc"
        )
        rs.execute()

    def test_resourcesync_with_oaipmh_generator_and_config_file(self):
        rs = ResourceSync(
            config_name="DEFAULT"
        )
        rs.execute()

if __name__ == "__main__":
    unittest.main()
