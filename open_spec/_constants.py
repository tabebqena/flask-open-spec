#
#
#
PATH_PARAMETERS_INTRO = """
#################### AUTOGENERATED ######################################################
# This file contains the API paramaters, for each request mapped to the 
# requrst_path and the request method.
# #######################################################################################
# You can edit this file, your edits will be preserved.
# schema:
# path/to/route:
#   method:          # COMMENT: one of the valid HTTP methods. in lower case.
#    -  in: null     # COMMENT: where the request data will send? 
#                    #          valid values=["query", "header", or "cookie"]
#       name: ""     # COMMENT: parameter name ex:. 'pet_id'
#       schema:  ""  # The import name of the schema that provide the parameter type
                     # ex:. project.module.MySchema 
                     # or dictionary of the parameter properties:
                     # ex:. {
                     #    type: 
                     #    format: uuid
                     #    enum: [0, 1]
                     #    default: 0
                     #    minimum: 1
                     #    maximum: 100
                     # }
#       description: ""
# N.B:. All parameters in=path are required, and autogenerated, You can update.
# N.B:. Add all other parameters from other locations, [query, header, cookie]
##########################################################\n
"""


REQUEST_SCHEMAS_INTRO = """
#################################################################################
################################# Autogenerared. ################################
# You can edit this file, your edits will be preserved.
# schema:
# path/to/route: 
#   method:          # COMMENT: one of the valid HTTP methods. in lower case.
#        description: ""
#        required: true or false
#        content:  
#           COMMENT: The key is the media type, 
#                    The value is the import path of the used schema 
#  
#           application/json: 
#                 schema: None   # COMMENT: each schema is represented by its Name
#           application/xml: 
#                 schema: None   # COMMENT: each schema is represented by its Name
#           application/x-www-form-urlencoded:None 
#                 schema: None   # COMMENT: each schema is represented by its Name
#           text/plain: 
#                 schema: None   # COMMENT: each schema is represented by its Name
# N.B:. add whatever media type you need, You can delete what is not applicable in your case
# N.B:. You can use oneOf or anyOf as you need
##################################################################################\n
"""

RESPONSE_MAPPING_INTRO = """
#################################################################################
################################# Autogenerared. ################################
# You can edit this file, your edits will be preserved.
# schema:
# path/to/route: 
#   method:          # COMMENT: one of the valid HTTP methods. in lower case.
#        description: ""
#        content:  
#           COMMENT: The key is the media type, 
#                    The value is the import path of the used schema 
#  
#           application/json: None # COMMENT: The import path of the used schema  
#                                  # COMMENT: ex: myproject.mymodule.MySchema
#           application/xml: None # COMMENT: The import path of the used schema  
#                                  # COMMENT: ex: myproject.mymodule.MySchema
#           application/x-www-form-urlencoded:None # COMMENT: The import path of the used schema  
#                                  # COMMENT: ex: myproject.mymodule.MySchema
#           text/plain: None # COMMENT: The import path of the used schema  
#                                  # COMMENT: ex: myproject.mymodule.MySchema
# N.B:. add whatever media type you need, You can delete what is not applicable in your case
##################################################################################\n"""

REQUEST_STUB = dict(
    description="",
    required=False,
    content={
        "application/json": {
            "schema": None,
            "example": {
                "summary": "",
                "description": "",
                "value": None,
                "externalValue": None,
            },
            "examples": {},
            "encoding": {
                "contentType": None,
                "headers": {},
            },
        },
    },
)


RESPONSE_STUB = {
    "default": {
        "description": "",
        "headers": {},
        "content": {"application/json": {"schema": None}},
        "links": {},
    },
    "200": {
        "description": "",
        "content": {"application/json": {"schema": None}},
    },
}
##
##
OAS_STUB = {
    "openapi": "3.0.2",
    "info": {"$ref": "info.yaml"},
    "servers": {"$ref": "servers.yaml"},
    "paths": {},  # no ref
    "components": {"$ref": "components.yaml"},
    "security": {"$ref": "security.yaml"},
    "tags": {"$ref": "tags.yaml"},
    "externalDocs": {"$ref": "externalDocs.yaml"},
}
#
#
INFO_INTRO = """
#################################################################################
################################# Autogenerared. ################################
# You can edit this file, your edits will be preserved.
# Put your INFO here.    
# ##################################################################################\n
"""
INFO_STUB = {
    "title": "",
    "description": "",
    "termsOfService": "",
    "contact": {
        "name": "",
        "url": "",
        "email": "",
    },
    "license": {
        "name": "",
        "url": "",
    },
    "version": "1.0",
}
#
#
TAGS_INTRO = """
#################################################################################
################################# Autogenerared. ################################
# You can edit this file, your edits will be preserved.
# Put your tags here, and use it in paths file.
# schema:
#   - name : tag_name
#     description: tag_description    
# ##################################################################################\n
"""
TAGS_STUB = []
#
#
SERVERS_INTRO = """
#################################################################################
################################# Autogenerared. ################################
# You can edit this file, your edits will be preserved.
# Put your servers here.
# schema:
#   - url : server_name
#     description: server_description  
#     variables:                    # COMMENT: OPTIONAL
#         variable_name:
#                 prop: value
#                 prop: value
#                 prop: value
#         variable_name:
#                 prop: value
#                 prop: value
#                 prop: value  
# ##################################################################################\n
"""
SERVERS_STUB = [{"url": None, "description": ""}]
#
#
SECURITY_SCHEMAS_INTRO = """
#################################################################################
################################# Autogenerared. ################################
# You can edit this file, your edits will be preserved.
# Put your security schemas here.
# schema:
#   security_name:
#     name : schema_name   # REQUIRED 
#     type :               # apiKey, http, oauth2, openIdConnect  
#     description: server_description  
#     in    : # location of the apiKey, query, header, cookie
#     scheme:  
#     bearerFormat:   
# ##################################################################################\n
"""
SECURITY_SCHEMAS_STUB = {}
#
#
EXTERNALDOCS_STUB = {
    "description": None,
    "url": None,
}
###########
PATHS_ITEM_STUB = {
    "summary": "",
    "description": "",
    "servers": [],
    "parameters": [],
}
##################
OPERATION_STUB = {
    "summary": "",
    "description": "",
    "tags": [],
    "externalDocs": EXTERNALDOCS_STUB,
    "operationId": None,
    "servers": [],
    "deprecated": False,
    "security": [],
    "callbacks": {},
}
