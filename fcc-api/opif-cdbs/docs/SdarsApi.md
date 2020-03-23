# swagger_client.SdarsApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sdars_eeo_facility_facility_id_format_get**](SdarsApi.md#sdars_eeo_facility_facility_id_format_get) | **GET** /sdars/eeo/facility/{facilityID}.{format} | SDARS EEO
[**sdars_frn_frn_format_get**](SdarsApi.md#sdars_frn_frn_format_get) | **GET** /sdars/frn/{frn}.{format} | SDARS Entity Details
[**sdars_getall_format_get**](SdarsApi.md#sdars_getall_format_get) | **GET** /sdars/getall.{format} | Get All
[**sdars_licensee_address_update_json_post**](SdarsApi.md#sdars_licensee_address_update_json_post) | **POST** /sdars/licenseeAddress/update.json | Update licensee address

# **sdars_eeo_facility_facility_id_format_get**
> sdars_eeo_facility_facility_id_format_get(facility_id, format)

SDARS EEO

SDARS EEO

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SdarsApi()
facility_id = 'facility_id_example' # str | facilityID
format = 'format_example' # str | json,  xml

try:
    # SDARS EEO
    api_instance.sdars_eeo_facility_facility_id_format_get(facility_id, format)
except ApiException as e:
    print("Exception when calling SdarsApi->sdars_eeo_facility_facility_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **facility_id** | **str**| facilityID | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sdars_frn_frn_format_get**
> sdars_frn_frn_format_get(frn, format)

SDARS Entity Details

SDARS Entity Details

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SdarsApi()
frn = 'frn_example' # str | frn - length of 10 digits
format = 'format_example' # str | json,  xml

try:
    # SDARS Entity Details
    api_instance.sdars_frn_frn_format_get(frn, format)
except ApiException as e:
    print("Exception when calling SdarsApi->sdars_frn_frn_format_get: %s\n" % e)
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

# **sdars_getall_format_get**
> sdars_getall_format_get(format)

Get All

Get All

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SdarsApi()
format = 'format_example' # str | json,  xml

try:
    # Get All
    api_instance.sdars_getall_format_get(format)
except ApiException as e:
    print("Exception when calling SdarsApi->sdars_getall_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sdars_licensee_address_update_json_post**
> sdars_licensee_address_update_json_post(body)

Update licensee address

Update licensee address

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SdarsApi()
body = swagger_client.LicenseeAddressUpdatePost() # LicenseeAddressUpdatePost | Create address post data body.

try:
    # Update licensee address
    api_instance.sdars_licensee_address_update_json_post(body)
except ApiException as e:
    print("Exception when calling SdarsApi->sdars_licensee_address_update_json_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LicenseeAddressUpdatePost**](LicenseeAddressUpdatePost.md)| Create address post data body. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

