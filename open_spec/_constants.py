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
TAGS_STUB = []
SERVERS_STUB = [{"url": None, "description": ""}]
SECURITY_SCHEMAS_STUB = {}
EXTERNALDOCS_STUB = {
    "description": None,
    "url": None,
}
#
PATHS_ITEM_STUB_LONG = {
    "summary": "",
    "description": "",
    "servers": [],
    "parameters": [],
}
PATHS_ITEM_STUB_SHORT = {
    "summary": "",
}
##################
OPERATION_STUB_LONG = {
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

OPERATION_STUB_SHORT = {
    "summary": "",
}
#
REQUEST_STUB_LONG = dict(
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
REQUEST_STUB_SHORT = dict(
    # description="",
    required=False,
    content={
        "application/json": {
            "schema": None,
        },
    },
)
RESPONSE_STUB_LONG = {
    "default": {
        "description": "",
        "headers": {},
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                },
            },
        },
        "links": {},
    },
    "200": {
        "description": "",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                },
            }
        },
    },
}
RESPONSE_STUB_SHORT = {
    "default": {
        "description": "",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                },
            },
        },
    },
}


###########
