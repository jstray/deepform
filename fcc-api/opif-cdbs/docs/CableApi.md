# swagger_client.CableApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cable_communities_psid_psid_format_get**](CableApi.md#cable_communities_psid_psid_format_get) | **GET** /cable/communities/psid/{psid}.{format} | Cable Communities
[**cable_eeo_group_by_format_get**](CableApi.md#cable_eeo_group_by_format_get) | **GET** /cable/eeo/{groupBy}.{format} | Cable eeo
[**cable_empunitid_update_json_post**](CableApi.md#cable_empunitid_update_json_post) | **POST** /cable/empunitid/update.json | Modify Cable service employee units
[**cable_getall_format_get**](CableApi.md#cable_getall_format_get) | **GET** /cable/getall.{format} | Get All
[**cable_operator_address_update_json_post**](CableApi.md#cable_operator_address_update_json_post) | **POST** /cable/operatorAddress/update.json | Modify Cable operator address
[**cable_principal_address_update_json_post**](CableApi.md#cable_principal_address_update_json_post) | **POST** /cable/principalAddress/update.json | Modify Cable principal address
[**cable_psid_psid_format_get**](CableApi.md#cable_psid_psid_format_get) | **GET** /cable/psid/{psid}.{format} | Cable Details
[**cable_relationship_username_coalsid_format_get**](CableApi.md#cable_relationship_username_coalsid_format_get) | **GET** /cable/relationship/username/{COALSID}.{format} | Relationship Cable
[**cable_service_zipcodes_update_json_post**](CableApi.md#cable_service_zipcodes_update_json_post) | **POST** /cable/serviceZipcodes/update.json | Modify Cable service zip codes

# **cable_communities_psid_psid_format_get**
> cable_communities_psid_psid_format_get(psid, format)

Cable Communities

Cable Communities

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
psid = 'psid_example' # str | psid
format = 'format_example' # str | json,  xml

try:
    # Cable Communities
    api_instance.cable_communities_psid_psid_format_get(psid, format)
except ApiException as e:
    print("Exception when calling CableApi->cable_communities_psid_psid_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **psid** | **str**| psid | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_eeo_group_by_format_get**
> cable_eeo_group_by_format_get(group_by, emp_unit_id, format)

Cable eeo

Cable eeo

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
group_by = 'group_by_example' # str | Group the eeo data by either employee unit id or form numbers
emp_unit_id = ['emp_unit_id_example'] # list[str] | array of employee unit id(s)
format = 'format_example' # str | json,  xml

try:
    # Cable eeo
    api_instance.cable_eeo_group_by_format_get(group_by, emp_unit_id, format)
except ApiException as e:
    print("Exception when calling CableApi->cable_eeo_group_by_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_by** | **str**| Group the eeo data by either employee unit id or form numbers | 
 **emp_unit_id** | [**list[str]**](str.md)| array of employee unit id(s) | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_empunitid_update_json_post**
> cable_empunitid_update_json_post(body)

Modify Cable service employee units

Modify Cable service employee units

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
body = swagger_client.CableServiceEmpUnitsUpdatePost() # CableServiceEmpUnitsUpdatePost | Create cable service employee units post data body.

try:
    # Modify Cable service employee units
    api_instance.cable_empunitid_update_json_post(body)
except ApiException as e:
    print("Exception when calling CableApi->cable_empunitid_update_json_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CableServiceEmpUnitsUpdatePost**](CableServiceEmpUnitsUpdatePost.md)| Create cable service employee units post data body. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_getall_format_get**
> cable_getall_format_get(format)

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
api_instance = swagger_client.CableApi()
format = 'format_example' # str | json,  xml

try:
    # Get All
    api_instance.cable_getall_format_get(format)
except ApiException as e:
    print("Exception when calling CableApi->cable_getall_format_get: %s\n" % e)
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

# **cable_operator_address_update_json_post**
> cable_operator_address_update_json_post(body)

Modify Cable operator address

Modify Cable operator address

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
body = swagger_client.CableOperatorAddressUpdatePost() # CableOperatorAddressUpdatePost | Create cable operator address post data body.

try:
    # Modify Cable operator address
    api_instance.cable_operator_address_update_json_post(body)
except ApiException as e:
    print("Exception when calling CableApi->cable_operator_address_update_json_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CableOperatorAddressUpdatePost**](CableOperatorAddressUpdatePost.md)| Create cable operator address post data body. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_principal_address_update_json_post**
> cable_principal_address_update_json_post(body)

Modify Cable principal address

Modify Cable principal address

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
body = swagger_client.CablePrincipalAddressUpdatePost() # CablePrincipalAddressUpdatePost | Create cable principal address post data body.

try:
    # Modify Cable principal address
    api_instance.cable_principal_address_update_json_post(body)
except ApiException as e:
    print("Exception when calling CableApi->cable_principal_address_update_json_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CablePrincipalAddressUpdatePost**](CablePrincipalAddressUpdatePost.md)| Create cable principal address post data body. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_psid_psid_format_get**
> cable_psid_psid_format_get(psid, format)

Cable Details

Cable Details

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
psid = 'psid_example' # str | psid
format = 'format_example' # str | json,  xml

try:
    # Cable Details
    api_instance.cable_psid_psid_format_get(psid, format)
except ApiException as e:
    print("Exception when calling CableApi->cable_psid_psid_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **psid** | **str**| psid | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_relationship_username_coalsid_format_get**
> cable_relationship_username_coalsid_format_get(coalsid, format)

Relationship Cable

Relationship Cable

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
coalsid = 'coalsid_example' # str | COALS ID
format = 'format_example' # str | json,  xml

try:
    # Relationship Cable
    api_instance.cable_relationship_username_coalsid_format_get(coalsid, format)
except ApiException as e:
    print("Exception when calling CableApi->cable_relationship_username_coalsid_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **coalsid** | **str**| COALS ID | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cable_service_zipcodes_update_json_post**
> cable_service_zipcodes_update_json_post(body)

Modify Cable service zip codes

Modify Cable service zip codes

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CableApi()
body = swagger_client.CableServiceZipCodesUpdatePost() # CableServiceZipCodesUpdatePost | Create cable service zipcodes post data body.

try:
    # Modify Cable service zip codes
    api_instance.cable_service_zipcodes_update_json_post(body)
except ApiException as e:
    print("Exception when calling CableApi->cable_service_zipcodes_update_json_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CableServiceZipCodesUpdatePost**](CableServiceZipCodesUpdatePost.md)| Create cable service zipcodes post data body. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

