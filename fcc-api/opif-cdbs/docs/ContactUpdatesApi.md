# swagger_client.ContactUpdatesApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**contact_update_json_post**](ContactUpdatesApi.md#contact_update_json_post) | **POST** contact/update.json | Specify contactType as \&quot;MS\&quot; for Main Studio Contact and \&quot;CC\&quot; for Closed Caption Contact.

# **contact_update_json_post**
> contact_update_json_post(body)

Specify contactType as \"MS\" for Main Studio Contact and \"CC\" for Closed Caption Contact.

Specify contactType as \"MS\" for Main Studio Contact and \"CC\" for Closed Caption Contact. Allowed values for contactSourceServiceCode are \"TV\", \"AM\" and \"FM\" for Main Studio Contact and \"TV\" for Closed Captions.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ContactUpdatesApi()
body = swagger_client.MainStudioClosedCaptionUpdate() # MainStudioClosedCaptionUpdate | Specify contactType as "MS" for Main Studio Contact and "CC" for Closed Caption Contact. Allowed values for contactSourceServiceCode are "TV", "AM" and "FM" for Main Studio Contact and "TV" for Closed Captions.

try:
    # Specify contactType as \"MS\" for Main Studio Contact and \"CC\" for Closed Caption Contact.
    api_instance.contact_update_json_post(body)
except ApiException as e:
    print("Exception when calling ContactUpdatesApi->contact_update_json_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MainStudioClosedCaptionUpdate**](MainStudioClosedCaptionUpdate.md)| Specify contactType as &quot;MS&quot; for Main Studio Contact and &quot;CC&quot; for Closed Caption Contact. Allowed values for contactSourceServiceCode are &quot;TV&quot;, &quot;AM&quot; and &quot;FM&quot; for Main Studio Contact and &quot;TV&quot; for Closed Captions. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

