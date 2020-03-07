# swagger_client.RelationshipApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**relationship_frn_frn_format_get**](RelationshipApi.md#relationship_frn_frn_format_get) | **GET** /relationship/frn/{frn}.{format} | Relationship FRN

# **relationship_frn_frn_format_get**
> relationship_frn_frn_format_get(frn, format)

Relationship FRN

Relationship FRN

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.RelationshipApi()
frn = 'frn_example' # str | frn - length of 10 digits
format = 'format_example' # str | json,  xml

try:
    # Relationship FRN
    api_instance.relationship_frn_frn_format_get(frn, format)
except ApiException as e:
    print("Exception when calling RelationshipApi->relationship_frn_frn_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **frn** | **str**| frn - length of 10 digits | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

