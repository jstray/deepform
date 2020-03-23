# swagger_client.FileApi

All URIs are relative to */api/manager*

Method | HTTP request | Description
------------- | ------------- | -------------
[**entity_logo_upload_post**](FileApi.md#entity_logo_upload_post) | **POST** /entity/logo/upload | Upload logo
[**file_history_count_jsonentity_identity_id_get**](FileApi.md#file_history_count_jsonentity_identity_id_get) | **GET** /file/historyCount.json?entityId&#x3D;{entityId} | Count of Files changes
[**file_history_format_get**](FileApi.md#file_history_format_get) | **GET** /file/history.{format} | List changed files
[**file_id_file_id_format_get**](FileApi.md#file_id_file_id_format_get) | **GET** /file/id/{fileId}.{format} | Get File Details
[**file_move_format_put**](FileApi.md#file_move_format_put) | **PUT** /file/move.{format} | Move File 
[**file_purge_file_id_entity_id_service_code_format_delete**](FileApi.md#file_purge_file_id_entity_id_service_code_format_delete) | **DELETE** /file/purge/{fileId}/{entityId}/{serviceCode}.{format} | Purge File
[**file_remove_file_id_entity_id_service_code_format_delete**](FileApi.md#file_remove_file_id_entity_id_service_code_format_delete) | **DELETE** /file/remove/{fileId}/{entityId}/{serviceCode}.{format} | Remove File
[**file_rename_format_put**](FileApi.md#file_rename_format_put) | **PUT** /file/rename.{format} | Rename File 
[**file_restore_format_put**](FileApi.md#file_restore_format_put) | **PUT** /file/restore.{format} | Restore File 
[**file_upload_format_post**](FileApi.md#file_upload_format_post) | **POST** /file/upload.{format} | Upload file

# **entity_logo_upload_post**
> entity_logo_upload_post(image, entity_id, service_code, access_token)

Upload logo

Upload logo file in jpeg/jpg, png or gif or tiff format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
image = 'image_example' # str | 
entity_id = 'entity_id_example' # str | 
service_code = 'service_code_example' # str | 
access_token = 'access_token_example' # str | API Access Key.

try:
    # Upload logo
    api_instance.entity_logo_upload_post(image, entity_id, service_code, access_token)
except ApiException as e:
    print("Exception when calling FileApi->entity_logo_upload_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image** | **str**|  | 
 **entity_id** | **str**|  | 
 **service_code** | **str**|  | 
 **access_token** | **str**| API Access Key. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_history_count_jsonentity_identity_id_get**
> list[FileHistoryCount] file_history_count_jsonentity_identity_id_get(entity_id, format)

Count of Files changes

Count files that were modified.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
entity_id = 'entity_id_example' # str | Unique Entity Id.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Count of Files changes
    api_response = api_instance.file_history_count_jsonentity_identity_id_get(entity_id, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_history_count_jsonentity_identity_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_id** | **str**| Unique Entity Id. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**list[FileHistoryCount]**](FileHistoryCount.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_history_format_get**
> list[FileHistory] file_history_format_get(format, count=count, entity_id=entity_id, start_date=start_date, end_date=end_date, offset=offset, status=status)

List changed files

Lists files that were modified.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml
count = 56 # int | Number of files in the list. (optional)
entity_id = 'entity_id_example' # str | Unique Entity Id. (optional)
start_date = '2013-10-20' # date | Date in ISO-8601 format.<br /><br />YYYY-MM-DD (eg 2015-08-25) (optional)
end_date = '2013-10-20' # date | Date in ISO-8601 format.<br /><br />YYYY-MM-DD (eg 2015-08-25) (optional)
offset = 56 # int | Starting row number (optional)
status = 'status_example' # str | File Status (optional)

try:
    # List changed files
    api_response = api_instance.file_history_format_get(format, count=count, entity_id=entity_id, start_date=start_date, end_date=end_date, offset=offset, status=status)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_history_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 
 **count** | **int**| Number of files in the list. | [optional] 
 **entity_id** | **str**| Unique Entity Id. | [optional] 
 **start_date** | **date**| Date in ISO-8601 format.&lt;br /&gt;&lt;br /&gt;YYYY-MM-DD (eg 2015-08-25) | [optional] 
 **end_date** | **date**| Date in ISO-8601 format.&lt;br /&gt;&lt;br /&gt;YYYY-MM-DD (eg 2015-08-25) | [optional] 
 **offset** | **int**| Starting row number | [optional] 
 **status** | **str**| File Status | [optional] 

### Return type

[**list[FileHistory]**](FileHistory.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_id_file_id_format_get**
> File file_id_file_id_format_get(file_id, entity_id, format)

Get File Details

Returns the file information for the specified file id.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
file_id = 'file_id_example' # str | Unique Id of the file.
entity_id = 'entity_id_example' # str | Unique Entity Id.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Get File Details
    api_response = api_instance.file_id_file_id_format_get(file_id, entity_id, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_id_file_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| Unique Id of the file. | 
 **entity_id** | **str**| Unique Entity Id. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**File**](File.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_move_format_put**
> object file_move_format_put(body, access_token, format)

Move File 

Move the file to a new folder location.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
body = swagger_client.FileMovePost() # FileMovePost | File move post data body.
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Move File 
    api_response = api_instance.file_move_format_put(body, access_token, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_move_format_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FileMovePost**](FileMovePost.md)| File move post data body. | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_purge_file_id_entity_id_service_code_format_delete**
> str file_purge_file_id_entity_id_service_code_format_delete(file_id, entity_id, format, access_token, service_code)

Purge File

Mark file as purged.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
file_id = 'file_id_example' # str | Unique Id of the file.
entity_id = 'entity_id_example' # str | Unique Id of the entity.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml
access_token = 'access_token_example' # str | API Access Key.
service_code = 'service_code_example' # str | Entity Service Code

try:
    # Purge File
    api_response = api_instance.file_purge_file_id_entity_id_service_code_format_delete(file_id, entity_id, format, access_token, service_code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_purge_file_id_entity_id_service_code_format_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| Unique Id of the file. | 
 **entity_id** | **str**| Unique Id of the entity. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 
 **access_token** | **str**| API Access Key. | 
 **service_code** | **str**| Entity Service Code | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_remove_file_id_entity_id_service_code_format_delete**
> str file_remove_file_id_entity_id_service_code_format_delete(file_id, entity_id, format, access_token, service_code)

Remove File

Mark file as deleted.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
file_id = 'file_id_example' # str | Unique Id of the file.
entity_id = 'entity_id_example' # str | Unique Id of the entity.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml
access_token = 'access_token_example' # str | API Access Key.
service_code = 'service_code_example' # str | Entity Service Code

try:
    # Remove File
    api_response = api_instance.file_remove_file_id_entity_id_service_code_format_delete(file_id, entity_id, format, access_token, service_code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_remove_file_id_entity_id_service_code_format_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| Unique Id of the file. | 
 **entity_id** | **str**| Unique Id of the entity. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 
 **access_token** | **str**| API Access Key. | 
 **service_code** | **str**| Entity Service Code | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_rename_format_put**
> File file_rename_format_put(body, access_token, format)

Rename File 

Rename the file with specified file name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
body = swagger_client.FileRenamePost() # FileRenamePost | File rename post data body.
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Rename File 
    api_response = api_instance.file_rename_format_put(body, access_token, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_rename_format_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FileRenamePost**](FileRenamePost.md)| File rename post data body. | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**File**](File.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_restore_format_put**
> File file_restore_format_put(body, access_token, format)

Restore File 

Restore the file with the specified id.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
body = swagger_client.FileRestorePost() # FileRestorePost | File restore post data body.
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Restore File 
    api_response = api_instance.file_restore_format_put(body, access_token, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileApi->file_restore_format_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FileRestorePost**](FileRestorePost.md)| File restore post data body. | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**File**](File.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **file_upload_format_post**
> file_upload_format_post(upload, parent_folder_id, entity_id, service_code, access_token, format)

Upload file

Upload file.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FileApi()
upload = 'upload_example' # str | 
parent_folder_id = 'parent_folder_id_example' # str | 
entity_id = 'entity_id_example' # str | 
service_code = 'service_code_example' # str | 
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Upload file
    api_instance.file_upload_format_post(upload, parent_folder_id, entity_id, service_code, access_token, format)
except ApiException as e:
    print("Exception when calling FileApi->file_upload_format_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upload** | **str**|  | 
 **parent_folder_id** | **str**|  | 
 **entity_id** | **str**|  | 
 **service_code** | **str**|  | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

