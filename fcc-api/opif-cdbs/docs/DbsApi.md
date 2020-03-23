# swagger_client.DbsApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dbs_eeo_facility_facility_id_format_get**](DbsApi.md#dbs_eeo_facility_facility_id_format_get) | **GET** /dbs/eeo/facility/{facilityID}.{format} | DBS EEO
[**dbs_frn_frn_format_get**](DbsApi.md#dbs_frn_frn_format_get) | **GET** /dbs/frn/{frn}.{format} | DBS Entity Details
[**dbs_getall_format_get**](DbsApi.md#dbs_getall_format_get) | **GET** /dbs/getall.{format} | Get All
[**dbs_licensee_address_update_json_post**](DbsApi.md#dbs_licensee_address_update_json_post) | **POST** /dbs/licenseeAddress/update.json | Update licensee address

# **dbs_eeo_facility_facility_id_format_get**
> dbs_eeo_facility_facility_id_format_get(facility_id, format)

DBS EEO

DBS EEO

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DbsApi()
facility_id = 'facility_id_example' # str | facilityID
format = 'format_example' # str | json,  xml

try:
    # DBS EEO
    api_instance.dbs_eeo_facility_facility_id_format_get(facility_id, format)
except ApiException as e:
    print("Exception when calling DbsApi->dbs_eeo_facility_facility_id_format_get: %s\n" % e)
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

# **dbs_frn_frn_format_get**
> dbs_frn_frn_format_get(frn, format)

DBS Entity Details

DBS Entity Details

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DbsApi()
frn = 'frn_example' # str | frn - length of 10 digits
format = 'format_example' # str | json,  xml

try:
    # DBS Entity Details
    api_instance.dbs_frn_frn_format_get(frn, format)
except ApiException as e:
    print("Exception when calling DbsApi->dbs_frn_frn_format_get: %s\n" % e)
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

# **dbs_getall_format_get**
> dbs_getall_format_get(format)

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
api_instance = swagger_client.DbsApi()
format = 'format_example' # str | json,  xml

try:
    # Get All
    api_instance.dbs_getall_format_get(format)
except ApiException as e:
    print("Exception when calling DbsApi->dbs_getall_format_get: %s\n" % e)
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

# **dbs_licensee_address_update_json_post**
> dbs_licensee_address_update_json_post(body)

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
api_instance = swagger_client.DbsApi()
body = swagger_client.LicenseeAddressUpdatePost() # LicenseeAddressUpdatePost | Create address post data body.

try:
    # Update licensee address
    api_instance.dbs_licensee_address_update_json_post(body)
except ApiException as e:
    print("Exception when calling DbsApi->dbs_licensee_address_update_json_post: %s\n" % e)
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

