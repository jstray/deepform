# swagger_client.SearchApi

All URIs are relative to *https://www.fcc.gov/search/api?t&#x3D;opif&amp;*

Method | HTTP request | Description
------------- | ------------- | -------------
[**qkeywordsoffsetoorderffilters_get**](SearchApi.md#qkeywordsoffsetoorderffilters_get) | **GET** q&#x3D;{keyword}&amp;s&#x3D;{offset}&amp;o&#x3D;{order}&amp;f&#x3D;{filters} | Search File Names

# **qkeywordsoffsetoorderffilters_get**
> qkeywordsoffsetoorderffilters_get(keyword, offset, order, filters)

Search File Names

Search file names of the uploaded documents in the OPIF system.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SearchApi()
keyword = 'keyword_example' # str | Keyword.
offset = 'offset_example' # str | Search results starting number.
order = 'order_example' # str | Sorting parameter.
filters = 'filters_example' # str | JSON array of Filters. See Filter descriptions below.

try:
    # Search File Names
    api_instance.qkeywordsoffsetoorderffilters_get(keyword, offset, order, filters)
except ApiException as e:
    print("Exception when calling SearchApi->qkeywordsoffsetoorderffilters_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **keyword** | **str**| Keyword. | 
 **offset** | **str**| Search results starting number. | 
 **order** | **str**| Sorting parameter. | 
 **filters** | **str**| JSON array of Filters. See Filter descriptions below. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

