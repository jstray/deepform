# swagger_client.SearchApi

All URIs are relative to */api/manager*

Method | HTTP request | Description
------------- | ------------- | -------------
[**search_key_search_key_format_get**](SearchApi.md#search_key_search_key_format_get) | **GET** /search/key/{searchKey}.{format} | Search for files and folders

# **search_key_search_key_format_get**
> SearchResult search_key_search_key_format_get(search_key, entity_id, format)

Search for files and folders

Search for files and folders based on specified searchKey

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SearchApi()
search_key = 'search_key_example' # str | Search key parameter
entity_id = 'entity_id_example' # str | Unique Entity Id.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Search for files and folders
    api_response = api_instance.search_key_search_key_format_get(search_key, entity_id, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SearchApi->search_key_search_key_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_key** | **str**| Search key parameter | 
 **entity_id** | **str**| Unique Entity Id. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**SearchResult**](SearchResult.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

