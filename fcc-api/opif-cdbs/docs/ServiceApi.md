# swagger_client.ServiceApi

All URIs are relative to */api/service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**service_type_applications_facility_entity_id_format_get**](ServiceApi.md#service_type_applications_facility_entity_id_format_get) | **GET** /{serviceType}/applications/facility/{entityID}.{format} | Entity Applications
[**service_type_eeo_facilityid_entity_id_format_get**](ServiceApi.md#service_type_eeo_facilityid_entity_id_format_get) | **GET** /{serviceType}/eeo/facilityid/{entityID}.{format} | Entity EEO
[**service_type_facility_getall_format_get**](ServiceApi.md#service_type_facility_getall_format_get) | **GET** /{serviceType}/facility/getall.{format} | Get All
[**service_type_facility_id_entity_id_format_get**](ServiceApi.md#service_type_facility_id_entity_id_format_get) | **GET** /{serviceType}/facility/id/{entityID}.{format} | Entity Details
[**service_type_ownership_facilityid_entity_id_format_get**](ServiceApi.md#service_type_ownership_facilityid_entity_id_format_get) | **GET** /{serviceType}/ownership/facilityid/{entityID}.{format} | Entity Ownership
[**service_type_relationship_frn_frn_format_get**](ServiceApi.md#service_type_relationship_frn_frn_format_get) | **GET** /{serviceType}/relationship/frn/{frn}.{format} | Relationship FRN

# **service_type_applications_facility_entity_id_format_get**
> service_type_applications_facility_entity_id_format_get(service_type, entity_id, format)

Entity Applications

Entity Applications

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ServiceApi()
service_type = 'service_type_example' # str | serviceType.<br /><br />Valid values: tv, fm, am
entity_id = 'entity_id_example' # str | Entity ID
format = 'format_example' # str | json,  xml

try:
    # Entity Applications
    api_instance.service_type_applications_facility_entity_id_format_get(service_type, entity_id, format)
except ApiException as e:
    print("Exception when calling ServiceApi->service_type_applications_facility_entity_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_type** | **str**| serviceType.&lt;br /&gt;&lt;br /&gt;Valid values: tv, fm, am | 
 **entity_id** | **str**| Entity ID | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **service_type_eeo_facilityid_entity_id_format_get**
> service_type_eeo_facilityid_entity_id_format_get(service_type, entity_id, format)

Entity EEO

Entity EEO

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ServiceApi()
service_type = 'service_type_example' # str | serviceType.<br /><br />Valid values: tv, fm, am
entity_id = 'entity_id_example' # str | Entity ID
format = 'format_example' # str | json,  xml

try:
    # Entity EEO
    api_instance.service_type_eeo_facilityid_entity_id_format_get(service_type, entity_id, format)
except ApiException as e:
    print("Exception when calling ServiceApi->service_type_eeo_facilityid_entity_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_type** | **str**| serviceType.&lt;br /&gt;&lt;br /&gt;Valid values: tv, fm, am | 
 **entity_id** | **str**| Entity ID | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **service_type_facility_getall_format_get**
> service_type_facility_getall_format_get(service_type, format)

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
api_instance = swagger_client.ServiceApi()
service_type = 'service_type_example' # str | serviceType.<br /><br />Valid values: tv, fm and am
format = 'format_example' # str | json,  xml

try:
    # Get All
    api_instance.service_type_facility_getall_format_get(service_type, format)
except ApiException as e:
    print("Exception when calling ServiceApi->service_type_facility_getall_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_type** | **str**| serviceType.&lt;br /&gt;&lt;br /&gt;Valid values: tv, fm and am | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **service_type_facility_id_entity_id_format_get**
> service_type_facility_id_entity_id_format_get(service_type, entity_id, format)

Entity Details

Entity Details

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ServiceApi()
service_type = 'service_type_example' # str | serviceType.<br /><br />Valid values: tv, fm, am
entity_id = 'entity_id_example' # str | Entity ID
format = 'format_example' # str | json,  xml

try:
    # Entity Details
    api_instance.service_type_facility_id_entity_id_format_get(service_type, entity_id, format)
except ApiException as e:
    print("Exception when calling ServiceApi->service_type_facility_id_entity_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_type** | **str**| serviceType.&lt;br /&gt;&lt;br /&gt;Valid values: tv, fm, am | 
 **entity_id** | **str**| Entity ID | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **service_type_ownership_facilityid_entity_id_format_get**
> service_type_ownership_facilityid_entity_id_format_get(service_type, entity_id, format)

Entity Ownership

Entity Ownership

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ServiceApi()
service_type = 'service_type_example' # str | serviceType.<br /><br />Valid values: tv, fm, am
entity_id = 'entity_id_example' # str | Entity ID
format = 'format_example' # str | json,  xml

try:
    # Entity Ownership
    api_instance.service_type_ownership_facilityid_entity_id_format_get(service_type, entity_id, format)
except ApiException as e:
    print("Exception when calling ServiceApi->service_type_ownership_facilityid_entity_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_type** | **str**| serviceType.&lt;br /&gt;&lt;br /&gt;Valid values: tv, fm, am | 
 **entity_id** | **str**| Entity ID | 
 **format** | **str**| json,  xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **service_type_relationship_frn_frn_format_get**
> service_type_relationship_frn_frn_format_get(service_type, frn, format)

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
api_instance = swagger_client.ServiceApi()
service_type = 'service_type_example' # str | serviceType.<br /><br />Valid values: tv, fm, am
frn = 'frn_example' # str | frn - length of 10 digits
format = 'format_example' # str | json, xml

try:
    # Relationship FRN
    api_instance.service_type_relationship_frn_frn_format_get(service_type, frn, format)
except ApiException as e:
    print("Exception when calling ServiceApi->service_type_relationship_frn_frn_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_type** | **str**| serviceType.&lt;br /&gt;&lt;br /&gt;Valid values: tv, fm, am | 
 **frn** | **str**| frn - length of 10 digits | 
 **format** | **str**| json, xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

