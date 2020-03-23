# swagger_client.FolderApi

All URIs are relative to */api/manager*

Method | HTTP request | Description
------------- | ------------- | -------------
[**folder_create_format_post**](FolderApi.md#folder_create_format_post) | **POST** /folder/create.{format} | Create new folder
[**folder_delete_folder_id_entity_id_service_code_format_delete**](FolderApi.md#folder_delete_folder_id_entity_id_service_code_format_delete) | **DELETE** /folder/delete/{folderId}/{entityId}/{serviceCode}.{format} | Delete Folder
[**folder_history_count_jsonentity_identity_id_get**](FolderApi.md#folder_history_count_jsonentity_identity_id_get) | **GET** /folder/historyCount.json?entityId&#x3D;{entityId} | Count of Folder changes
[**folder_history_format_get**](FolderApi.md#folder_history_format_get) | **GET** /folder/history.{format} | Folder changes list
[**folder_id_folder_id_format_get**](FolderApi.md#folder_id_folder_id_format_get) | **GET** /folder/id/{folderId}.{format} | Get Subfolder and files
[**folder_more_public_folders_format_get**](FolderApi.md#folder_more_public_folders_format_get) | **GET** /folder/morePublicFolders.{format} | Get More Public Folders 
[**folder_parent_folders_format_get**](FolderApi.md#folder_parent_folders_format_get) | **GET** /folder/parentFolders.{format} | Get parent folders
[**folder_path_format_get**](FolderApi.md#folder_path_format_get) | **GET** /folder/path.{format} | Get Folder for specified path.
[**folder_purge_folder_id_entity_id_service_code_format_delete**](FolderApi.md#folder_purge_folder_id_entity_id_service_code_format_delete) | **DELETE** /folder/purge/{folderId}/{entityId}/{serviceCode}.{format} | Purge Folder
[**folder_rename_format_put**](FolderApi.md#folder_rename_format_put) | **PUT** /folder/rename.{format} | Rename Folder
[**folder_restore_format_put**](FolderApi.md#folder_restore_format_put) | **PUT** /folder/restore.{format} | Restore Folder

# **folder_create_format_post**
> FolderCreate folder_create_format_post(body, access_token, format)

Create new folder

Create new folder with the folder details specified.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
body = swagger_client.FolderCreatePost() # FolderCreatePost | Create folder post data body.
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Create new folder
    api_response = api_instance.folder_create_format_post(body, access_token, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_create_format_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FolderCreatePost**](FolderCreatePost.md)| Create folder post data body. | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**FolderCreate**](FolderCreate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_delete_folder_id_entity_id_service_code_format_delete**
> str folder_delete_folder_id_entity_id_service_code_format_delete(folder_id, entity_id, format, access_token, service_code)

Delete Folder

Mark the specified folder as deleted.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
folder_id = 'folder_id_example' # str | Unique Id of the folder.
entity_id = 'entity_id_example' # str | Unique Id of the entity.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml
access_token = 'access_token_example' # str | API Access Key.
service_code = 'service_code_example' # str | Entity Service Code

try:
    # Delete Folder
    api_response = api_instance.folder_delete_folder_id_entity_id_service_code_format_delete(folder_id, entity_id, format, access_token, service_code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_delete_folder_id_entity_id_service_code_format_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| Unique Id of the folder. | 
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

# **folder_history_count_jsonentity_identity_id_get**
> list[FolderHistoryCount] folder_history_count_jsonentity_identity_id_get(entity_id, format)

Count of Folder changes

Count folders that were modified.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
entity_id = 'entity_id_example' # str | Unique Entity Id.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Count of Folder changes
    api_response = api_instance.folder_history_count_jsonentity_identity_id_get(entity_id, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_history_count_jsonentity_identity_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_id** | **str**| Unique Entity Id. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**list[FolderHistoryCount]**](FolderHistoryCount.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_history_format_get**
> list[FolderHistory] folder_history_format_get(format, count=count, entity_id=entity_id, start_date=start_date, end_date=end_date, offset=offset, status=status)

Folder changes list

Lists folders that were modified.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml
count = 56 # int | Number of folders in the list. (optional)
entity_id = 'entity_id_example' # str | Unique Entity Id. (optional)
start_date = '2013-10-20' # date | Date in ISO-8601 format.<br /><br />YYYY-MM-DD (eg 2015-08-25) (optional)
end_date = '2013-10-20' # date | Date in ISO-8601 format.<br /><br />YYYY-MM-DD (eg 2015-08-25) (optional)
offset = 56 # int | Starting row number (optional)
status = 'status_example' # str | Folder Status (optional)

try:
    # Folder changes list
    api_response = api_instance.folder_history_format_get(format, count=count, entity_id=entity_id, start_date=start_date, end_date=end_date, offset=offset, status=status)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_history_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 
 **count** | **int**| Number of folders in the list. | [optional] 
 **entity_id** | **str**| Unique Entity Id. | [optional] 
 **start_date** | **date**| Date in ISO-8601 format.&lt;br /&gt;&lt;br /&gt;YYYY-MM-DD (eg 2015-08-25) | [optional] 
 **end_date** | **date**| Date in ISO-8601 format.&lt;br /&gt;&lt;br /&gt;YYYY-MM-DD (eg 2015-08-25) | [optional] 
 **offset** | **int**| Starting row number | [optional] 
 **status** | **str**| Folder Status | [optional] 

### Return type

[**list[FolderHistory]**](FolderHistory.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_id_folder_id_format_get**
> Entity folder_id_folder_id_format_get(folder_id, entity_id, format)

Get Subfolder and files

Get OPIF folder information including list of subfolders and files. Response returned in specified format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
folder_id = 'folder_id_example' # str | Unique Id of the folder.
entity_id = 'entity_id_example' # str | Unique Entity Id.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Get Subfolder and files
    api_response = api_instance.folder_id_folder_id_format_get(folder_id, entity_id, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_id_folder_id_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| Unique Id of the folder. | 
 **entity_id** | **str**| Unique Entity Id. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**Entity**](Entity.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_more_public_folders_format_get**
> list[Folder] folder_more_public_folders_format_get(entity_id, source_service, format)

Get More Public Folders 

Get folders for the specified entityId in 'More Public Files'category. Response returned in specified format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
entity_id = 'entity_id_example' # str | Unique Entity Id.
source_service = 'source_service_example' # str | Source Service
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Get More Public Folders 
    api_response = api_instance.folder_more_public_folders_format_get(entity_id, source_service, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_more_public_folders_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_id** | **str**| Unique Entity Id. | 
 **source_service** | **str**| Source Service | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**list[Folder]**](Folder.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_parent_folders_format_get**
> list[Folder] folder_parent_folders_format_get(entity_id, source_service, format)

Get parent folders

Get root folder information including list of subfolders and files. Response returned in specified format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
entity_id = 'entity_id_example' # str | Unique Entity Id.
source_service = 'source_service_example' # str | Source Service
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Get parent folders
    api_response = api_instance.folder_parent_folders_format_get(entity_id, source_service, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_parent_folders_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_id** | **str**| Unique Entity Id. | 
 **source_service** | **str**| Source Service | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**list[Folder]**](Folder.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_path_format_get**
> Folder folder_path_format_get(folder_path, entity_id, source_service, format)

Get Folder for specified path.

Get OPIF folder information. Response returned in specified format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
folder_path = 'folder_path_example' # str | Complete folder path.
entity_id = 'entity_id_example' # str | Unique Entity Id.
source_service = 'source_service_example' # str | Source Service
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Get Folder for specified path.
    api_response = api_instance.folder_path_format_get(folder_path, entity_id, source_service, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_path_format_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_path** | **str**| Complete folder path. | 
 **entity_id** | **str**| Unique Entity Id. | 
 **source_service** | **str**| Source Service | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**Folder**](Folder.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_purge_folder_id_entity_id_service_code_format_delete**
> str folder_purge_folder_id_entity_id_service_code_format_delete(folder_id, entity_id, format, access_token, service_code)

Purge Folder

Purge the folder with the specified id.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
folder_id = 'folder_id_example' # str | Unique Id of the folder.
entity_id = 'entity_id_example' # str | Unique Id of the entity.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml
access_token = 'access_token_example' # str | API Access Key.
service_code = 'service_code_example' # str | Entity Service Code

try:
    # Purge Folder
    api_response = api_instance.folder_purge_folder_id_entity_id_service_code_format_delete(folder_id, entity_id, format, access_token, service_code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_purge_folder_id_entity_id_service_code_format_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| Unique Id of the folder. | 
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

# **folder_rename_format_put**
> FolderUpdate folder_rename_format_put(body, access_token, format)

Rename Folder

Rename the folder with the specified folder name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
body = swagger_client.FolderRenamePost() # FolderRenamePost | Rename folder post data body.
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Rename Folder
    api_response = api_instance.folder_rename_format_put(body, access_token, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_rename_format_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FolderRenamePost**](FolderRenamePost.md)| Rename folder post data body. | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**FolderUpdate**](FolderUpdate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **folder_restore_format_put**
> FolderUpdate folder_restore_format_put(body, access_token, format)

Restore Folder

Restore the status of the folder with the specified id.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FolderApi()
body = swagger_client.FolderPost() # FolderPost | Restore folder post data body.
access_token = 'access_token_example' # str | API Access Key.
format = 'format_example' # str | Format for the returned results.<br /><br />Valid values: json, jsonp, xml

try:
    # Restore Folder
    api_response = api_instance.folder_restore_format_put(body, access_token, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FolderApi->folder_restore_format_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FolderPost**](FolderPost.md)| Restore folder post data body. | 
 **access_token** | **str**| API Access Key. | 
 **format** | **str**| Format for the returned results.&lt;br /&gt;&lt;br /&gt;Valid values: json, jsonp, xml | 

### Return type

[**FolderUpdate**](FolderUpdate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json, application/jsonp, application/xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

