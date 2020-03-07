# swagger_client.FacilityApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**facility_search_keyword_format_get**](FacilityApi.md#facility_search_keyword_format_get) | **GET** /facility/search/{keyword}.{format} | Search

# **facility_search_keyword_format_get**
> facility_search_keyword_format_get(keyword, format)

Search

Search

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FacilityApi()
keyword = 'keyword_example' # str | 
format = 'format_example' # str | json,  xml

try:
    # Search
    api_instance.facility_search_keyword_format_get(keyword, format)
except ApiException as e:
    print("Exception when calling FacilityApi->facility_search_keyword_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **keyword** | **str**|  | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

