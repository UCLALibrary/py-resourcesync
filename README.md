# py-resourcesync [![Build Status](https://travis-ci.org/resourcesync/py-resourcesync.svg?branch=master)](https://travis-ci.org/resourcesync/py-resourcesync)


Core Python library for ResourceSync publishing

---
- Source location: [https://github.com/resourcesync/py-resourcesync](https://github.com/resourcesync/py-resourcesync)
- In case of questions [contact here](https://github.com/resourcesync/py-resourcesync/issues/new).

---

## Introduction
The [ResourceSync specification](http://www.openarchives.org/rs/1.0.9/resourcesync) describes 
a synchronization framework for the web consisting of various capabilities that allow third-party systems to remain synchronized with a server's evolving resources.
More precisely the ResourceSync Framework describes the communication between `source` and `destination` aimed at
synchronizing one or more resources. Communication uses `http` and an extension on 
the [Sitemap protocol](http://www.sitemaps.org/protocol.html), an xml-based format for expressing metadata relevant for synchronization.

The software in `py-resourcesync` library handles the `source`-side implementation of the framework.
Given a bunch of resources it analyzes these resources and the differences over time and creates
the necessary sitemap-documents that describe the resources and the changes. 

## Getting Started
### Installation from Source

Clone or downoad the source code and issue the install
command from the root directory of this project.

**Note**: This library requires Python >3.5 and is not compatible with Python 2.\* .
```
$ cd your/path/to/py-resourcesync
$ python3 setup.py install
```

### Resource Metadata

`py-resourcesync` will have to be provided with the necessary metadata 
 of the resources so that it can generate the appropriate ResourceSync documents. 
 The metadata source could be a filesystem, a database like MySQL or elasticsearch, an OAI-PMH 
 endpoint, or a REST API. The user of this library will have to implement this metadata provider 
 specific to your system so that `py-resourcesync` can call to retrieve the resource metadata. 
 We call this metadata provider a `Generator`. Generators for common metadata stores like the 
 ones mentioned above will be provided as part of this library in the near future. 
 
 To help understand what a generator might look like, a very basic example is provided in the 
 [`EgGenerator`](resourcesync/generators/eg_generator.py) class. The generator will have to 
 sub-class the `Generator` class and must implement the `generate` method. The `generate` method 
 must return an iterable or an iterator of 
 [resync/Resource](https://github.com/resync/resync/blob/master/resync/resource.py) instances.

### Generating ResourceSync Documents

Once the Generator has been implemented to provide the resource metadata to the library,
 the ResourceSync documents can be generated by invoking the `execute()` 
 method in the `ResourceSync` class 
 and providing it with the name of the generator class. 
 
```python
>>> from resourcesync.resourcesync import ResourceSync
>>> from my_generator import MyGenerator
>>> my_generator = MyGenerator()
>>> rs = ResourceSync()
>>> rs.generator = my_generator
>>> rs.execute()
```

The execute method will invoke the `generate()` method of the 
`MyGenerator` instance and obtain the list of resource metadata.

The library can be told what type of ResourceSync document to produce by 
passing the name of the resource type to the parameter `strategy`. 
The library currently supports 
`resourcelist`, `new_changelist`, and `inc_changelist`.

```python
>>> from resourcesync.resourcesync import ResourceSync
>>> from my_generator import MyGenerator
>>> my_generator = MyGenerator()
>>> rs = ResourceSync(generator=my_generator, 
                      strategy="resourcelist")
>>> rs.execute()
```

By default, the generated resourcesync documents are saved in a folder 
called `metadata` in the home directory of the user. The `resource_dir`
and the `metadata_dir` parameters can be used to change these. 

```python
>>> from resourcesync.resourcesync import ResourceSync
>>> from my_generator import MyGenerator
>>> my_generator = MyGenerator()
>>> rs = ResourceSync(generator=my_generator,
                      strategy="resourcelist",
                      resource_dir="/var/metadata/",
                      metadata_dir="resourcesync")
>>> rs.execute()
```
Now the generated ResourceSync documents will be stored in 
`/var/metadata/resourcesync`.

A brief explanation of all the available parameters are provided in the 
Parameters section below. 

## Architecture Overview

![Overview](img/comp_02.png)

_Fig. 1. Overview of the main features of `py-resourcesync`._

In essence py-resourcesync is a one-class, one-method library: class `ResourceSync`, method `execute`.
But there is more:

- `Parameters` control the conditions under which the execution takes place. Multiple sets of parameters can
be saved as configurations and restored from disk.
- The set of resources that will be synchronized can be selected and filtered using pluggable component
called `Generator`. The user can easily implement ways to select and filter metadata for resources for your system.
    - The `execute` method in the `ResourceSync` class will invoke the `generate` function of the custom 
    generator to retrieve the resource metadata. The custom generator must be a subclass of the `Generator` class.
    - The generator is responsible for selecting and filtering the necessary resources and gathering the 
    required metadata needed to build the ResourceSync documents.
    - The generator must return a list of [resync/Resource](https://github.com/resync/resync/blob/master/resync/resource.py) 
    instances when the called by the `ResourceSync.execute` method.
- The chosen `Strategy` determines what kind of process will do the synchronization. At the moment there are `Executors`
that produce _resourcelists_, _new changelists_ or _incremental changelists_.

A set of parameters, known as a configuration, can precisely define a set of resources, the selection and filter
mechanisms, the publication strategy and where to store the resourcesync metadata. Dedicated configurations can be defined
for multiple sets of resources and published in equal amounts of _capabilitylists_. A configuration can be saved on disk,
restored and run with a minimum effort. This makes `py-resourcesync` the ideal library for scripting a publication
strategy that will serve multiple groups of consumers that may be interested in different sets of resources offered
by your site.


## Parameters


`config_name`: The name of the configuration to read. If given, sets the current configuration. (str)

`resource_dir`: The local root directory for ResourceSync publishing (str)
    
`metadata_dir`: The directory name for ResourceSync documents (str)
    
`description_dir`: Directory where a version of the description document is kept (str)
    
`url_prefix`: The URL-prefix for ResourceSync publishing (str)

`document_root`: The directory from which the server will serve files (str)

`strategy`: Strategy for ResourceSync publishing (str | int | class `~resourcesync.parameters.enum.Strategy`)

`plugin_dir`: Directory where plugins can be found (str)

`max_items_in_list`: The maximum amount of records in a sitemap (int, 1 - 50000)

`zero_fill_filename`: The amount of digits in a sitemap filename (int, 1 - 10)

`is_saving_pretty_xml`: Determines appearance of sitemap xml (bool)

`is_saving_sitemaps`: Determines if sitemaps will be written to disk (bool)

`has_wellknown_at_root`: Where is the description document {.well-known/resourcesync} on the server (bool)


## OAI-PMH Generator

An OAI-PMH generator for py-resourcesync exists in `resourcesync/generators`, allowing institutions to bootstrap a ResourceSync-compatible repository using their existing OAI-PMH repository.

The code snippets below use filesystem paths for institutions that will be using `httpd` to serve their ResourceSync documents.

### Installation

In addition to the setup instructions [above](#installation-from-source), do the following:

```bash
$ pip3 install beautifulsoup4 Sickle validators
```

#### Testing

In order to run the tests for this generator, you'll also need to do:

```bash
$ pip3 install requests-mock
```

### Usage

There must exist a directory at the path specified by `resource_dir`. For `httpd`:

```bash
$ mkdir /var/www/html/resourcesync/ # create a place for the ResourceSync documents
```

Then, with Python:

```python
from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.oaipmh_generator import OAIPMHGenerator

httpd_document_root = '/var/www/html'
resource_dir = 'resourcesync'
collection_name = 'test'
resourcesync_url = 'http://your-resourcecync-server.edu'

# your-oaipmh-server may be the same as your-resourcesync-server
oaipmh_base_url = 'http://your-oaipmh-server.edu/oai/provider'

oaipmh_set = collection_name # or None, if the "set" parameter is not used in
                             # the query string for ListIdentifiers and
                             # ListRecords requests (i.e., each record set
                             # has a distinct base URL)

oaipmh_metadataprefix = 'oai_dc'

my_generator = OAIPMHGenerator(params={
    'oaipmh_base_url':       oaipmh_base_url,
    'oaipmh_set':            oaipmh_set,
    'oaipmh_metadataprefix': oaipmh_metadataprefix})

rs = ResourceSync(generator=my_generator,
                  strategy=0,
                  resource_dir='{}/{}'.format(httpd_document_root, resource_dir),
                  metadata_dir=collection_name,
                  description_dir=httpd_document_root,
                  url_prefix='{}/{}'.format(resourcesync_url, resource_dir),
                  is_saving_sitemaps=True)
rs.execute()
```


## Solr Generator

There is a generator for Apache Solr for py-resourcesync in `resourcesync/generators`. As with the OAI-PMH generator, the intent is to make it easier for institutions which may have indexed metadata using Solr, to bootstrap a ResourceSync-compatible repository.

The code snippets below use filesystem paths for institutions that will be using `httpd` to serve their ResourceSync documents.

### Installation

No additional libraries or installation steps are required.

#### Testing

Currently no tests are available.

### Usage

There must exist a directory at the path specified by `resource_dir`. For `httpd`:

```bash
$ mkdir /var/www/html/resourcesync/ # create a place for the ResourceSync documents
```

Then, with Python:

```python
from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.solr_generator import SolrGenerator

httpd_document_root = '/var/www/html'
resource_dir = 'resourcesync'
collection_name = 'test'
resourcesync_url = 'http://your-resourcecync-server.edu'

solr_base_url         = 'http://solr-server.edu/solr/some-collection/select?q='
solr_query            = '*'
solr_params           = '&wt=python&sort=recID+asc&cursorMark=_*_'
metadata_element      = 'recID'
metadata_disseminator = ''
time_element          = 'timestamp'
metadata_type         = 'dc'

solr_generator_params = {
            "solr_base_url":         solr_base_url,
            "solr_query":            solr_query,
            "solr_params":           solr_params,
            "metadata_identifier":   metadata_element,
            "metadata_disseminator": metadata_disseminator,
            "metadata_timestamp":    time_element,
            "metadata_type":         metadata_type}

s_generator = SolrGenerator(params=solr_generator_params)

rs = ResourceSync(generator=s_generator,
                  strategy=0,
                  resource_dir='{}/{}'.format(httpd_document_root, resource_dir),
                  metadata_dir=collection_name,
                  description_dir=httpd_document_root,
                  url_prefix='{}/{}'.format(resourcesync_url, resource_dir),
                  is_saving_sitemaps=True)
rs.execute()
```

### Notes

The Solr generator has been tested with Solr 5.x and Solr 6.1.0. The Solr generator parameters listed above correspond to labels for fields in the Solr result set. These will in all probability differ for different Solr installations. You will need to look at the raw Python-formatted output for some sample queries for the Solr instance you intend to make available via py-resourcesync to determine appropriate values.

There are a few things to be aware of: 

1. The Solr generator expects the Solr results set to be Python formatted (wt=python parameter)
2. The Solr generator cannot handle a multi-value date field. The timestamp label specified above should be associated with a single value per record. Out of the box, some instances of Solr generate dynamic multi-value timestamp fields by default.
3. metadata_type is not currently used
4. metadata_disseminator is only required when the metadata_element field contains a record identifier that requires a base URL before it can be resolved. If metadata_element contains full URLs, leave metadata_disseminator blank.
5. solr_query can be as simple as a wildcard or can reference a collection, specify a date range, etc. Refer to the documentation for the version of Solr you are running or use Solr admin to generate and test your query.
6. You will need to change part of the solr_params value so that the value for the Solr sort parameter corresponds to an indexed field in your instance of Solr.

## Elasticsearch generator

The [Elasticsearch generator](resourcesync/generators/elastic_generator.py) allows a flexible use of [Elasticsearch](https://www.elastic.co/) to keep track of the state of ResourceSync resources.
Data regarding resources and their changes must be recorded in Elasticsearch according to the protocol defined in the [documentation](resourcesync/generators/elastic/README.md).
The code snippets below use filesystem paths for institutions that will be using `httpd` to serve their ResourceSync documents.

**WARNING**: this generator has been tested on Elasticsearch v1.7.5. Subsequent versions may require different mapping
and queries.

### Installation

In addition to the setup instructions [above](#installation-from-source), do the following:
```bash
$ pip3 install 'elasticsearch>=1.0.0,<2.0.0'
```


#### Testing

In order to run the tests for this generator, you'll also need to do:

```bash
$ pip3 install urllib3-mock
```

### Usage

There must exist a directory at the path specified by `resource_dir`. For `httpd`:

```bash
$ mkdir /var/www/html/resourcesync/ # create a place for the ResourceSync documents
```

Then, with Python:

```python
from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.elastic_generator import ElasticGenerator

httpd_document_root = '/var/www/html'
resource_dir = 'resourcesync'
collection_name = 'foo-set'
resourcesync_url = 'http://your-resourcecync-server.edu'

url_prefix = '{}/{}'.format(resourcesync_url, resource_dir),
strategy = 0
max_items_in_list= 1000

params = {
            "resource_set": "foo-set",
            "resource_root_dir": "/resources/root/directory",
            "elastic_host": "localhost",
            "elastic_port": 9200,
            "elastic_index": "resync-index",
            "elastic_resource_doc_type": "resource",
            "elastic_change_doc_type": "change",
            "strategy": strategy,
            "url_prefix": url_prefix,
            "max_items_in_list": max_items_in_list
        }


my_generator = ElasticGenerator(params=params)

rs = ResourceSync(generator=my_generator,
                  strategy=strategy,
                  resource_dir='{}/{}'.format(httpd_document_root, resource_dir),
                  metadata_dir=collection_name,
                  description_dir=httpd_document_root,
                  url_prefix=url_prefix,
                  max_items_in_list=max_items_in_list,
                  is_saving_sitemaps=True)
rs.execute()
```
NOTE: further details on the generator's parameters available in the [documentation](resourcesync/generators/elastic/README.md)