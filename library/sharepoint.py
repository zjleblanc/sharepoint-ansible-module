#!/usr/bin/python
# -*- coding: utf-8 -*-


# Copyright: (c) 2022, DELGEHIER Cedric <cedric.delgehier@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import requests
import json
import os


__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


DOCUMENTATION = """
---
module: sharepoint
short_description: Upload, download, and delete files in Microsoft Sharepoint.
description:
  - Upload, download, and delete files in Microsoft Sharepoint.
version_added: "2.9"

options:
  client_id:
    type: str
    description:
      - The client_id is a public identifier for apps.
    required: true

  client_secret:
    type: str
    description:
      - The client_secret is a secret known only to the application and the authorization server. It is essential the application’s own password
    required: true

  grant_type:
    type: str
    description:
      - The grant method to use in the payload.
    choices:
      - client_credentials
    default: client_credentials

  local_file_name:
    type: str
    description:
      - Local filename to use.

  local_file_path:
    type: str
    description:
      - Local path to use.
    default: current directory

  remote_file_name:
    type: str
    description:
      - The remote filename.

  remote_file_path:
    type: str
    description:
      - The target folder remote path.
    required: true

  resource:
    type: str
    description:
      - The resource name to use in the payload. this is useful when the share is not "Office 365 SharePoint Online"

  site_name:
    type: str
    description:
      - The sharepoint site name to use (ex: tenant_name.sharepoint.com/sites/site_name)
    required: true

  tenant_id:
    type: str
    description:
      - The tenant ID used for oAuth.
    required: true

  tenant_name:
    type: str
    description:
      - The sharepoint tenant name to use (ex: tenant_name.sharepoint.com)
    required: true

author: "Cédric DELGEHIER (@cdelgehier)"
requirements:
  - json
  - requests
  - os
"""

EXAMPLES = """
- name: "Test sharepoint files"
  hosts: localhost
  gather_facts: false

  tasks:
    - name: "Push file to test folder"
      sharepoint:
        client_id: "B46D4098-D41D-4462-91BF-545DC75E9CEA"
        client_secret: "/7D99fe7a43394d4DA68377F432C3FF94="
        tenant_name: "mycompany"
        tenant_id: "F8A30A4A-1624-4D6E-8855-2A9F2E63E948"
        site_name: "Ops"

        local_file_path: "/Users/cdelgehier/Documents"
        local_file_name: "test.txt"
        remote_file_path: "/Shared Documents/Dev"

    - name: "Get file from sharepoint"
      sharepoint:
        method : get
        client_id: "B46D4098-D41D-4462-91BF-545DC75E9CEA"
        client_secret: "/7D99fe7a43394d4DA68377F432C3FF94="
        tenant_name: "mycompany"
        tenant_id: "F8A30A4A-1624-4D6E-8855-2A9F2E63E948"
        site_name: "Ops"

        remote_file_path: "/Shared Documents/Dev"
        remote_file_name: test.txt
        local_file_path: "/Users/cdelgehier/Documents"

    - name: "Delete file in sharepoint"
      sharepoint:
        method : delete
        client_id: "B46D4098-D41D-4462-91BF-545DC75E9CEA"
        client_secret: "/7D99fe7a43394d4DA68377F432C3FF94="
        tenant_name: "mycompany"
        tenant_id: "F8A30A4A-1624-4D6E-8855-2A9F2E63E948"
        site_name: "Ops"

        remote_file_path: "/Shared Documents/Dev"
        remote_file_name: test.txt

    - name: "List a folder"
      sharepoint:
        method : list
        client_id: "B46D4098-D41D-4462-91BF-545DC75E9CEA"
        client_secret: "/7D99fe7a43394d4DA68377F432C3FF94="
        tenant_name: "mycompany"
        tenant_id: "F8A30A4A-1624-4D6E-8855-2A9F2E63E948"
        site_name: "Ops"

        remote_file_path: "/Shared Documents/Dev"

    - name: "Create folder in sharepoint"
      sharepoint:
        method : mkdir
        client_id: "B46D4098-D41D-4462-91BF-545DC75E9CEA"
        client_secret: "/7D99fe7a43394d4DA68377F432C3FF94="
        tenant_name: "mycompany"
        tenant_id: "F8A30A4A-1624-4D6E-8855-2A9F2E63E948"
        site_name: "Ops"

        remote_file_path: "/Shared Documents/Dev/foo"

    - name: "Delete folder in sharepoint"
      sharepoint:
        method : rmdir
        client_id: "B46D4098-D41D-4462-91BF-545DC75E9CEA"
        client_secret: "/7D99fe7a43394d4DA68377F432C3FF94="
        tenant_name: "mycompany"
        tenant_id: "F8A30A4A-1624-4D6E-8855-2A9F2E63E948"
        site_name: "Ops"

        remote_file_path: "/Shared Documents/Dev/foo"

"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback

ODATA_SELECTORS = {
    "get": "$value",
    "metadata": "ListItemAllFields"
}

def main():

    argument_spec = dict(
        method=dict(
            type="str",
            default="put",
            choices=[
                "put",
                "get",
                "metadata",
                "delete",
                "list",
                "mkdir",
                "rmdir",
            ],
        ),
        local_file_path=dict(type="str", default=os.getcwd()),
        local_file_name=dict(type="str", required=False),
        remote_file_path=dict(type="str", required=True),
        remote_file_name=dict(type="str", required=False),
        client_id=dict(
            type="str",
            # required=True,
            fallback=(env_fallback, ["SHAREPOINT_CLIENT_ID"]),
        ),
        client_secret=dict(
            type="str",
            # required=True,
            no_log=True,
            fallback=(env_fallback, ["SHAREPOINT_CLIENT_SECRET"]),
        ),
        tenant_id=dict(
            type="str",
            # required=True,
            fallback=(env_fallback, ["SHAREPOINT_TENANT_ID"]),
        ),
        tenant_name=dict(
            type="str",
            # required=True,
            fallback=(env_fallback, ["SHAREPOINT_TENANT_NAME"]),
        ),
        site_name=dict(
            type="str",
            # required=True,
            fallback=(env_fallback, ["SHAREPOINT_SITE_NAME"]),
        ),
        resource=dict(type="str", required=False),
        grant_type=dict(
            type="str",
            default="client_credentials",
        ),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    # Extract our parameters
    method = module.params.get("method")
    local_file_path = module.params.get("local_file_path")
    local_file_name = module.params.get("local_file_name")
    if local_file_name is None and method == "get":
        local_file_name = module.params.get("remote_file_name")
    remote_file_path = module.params.get("remote_file_path")
    remote_file_name = module.params.get("remote_file_name")
    if remote_file_name is None and method == "put":
        remote_file_name = module.params.get("local_file_name")
    client_id = module.params.get("client_id")
    client_secret = module.params.get("client_secret")
    tenant_id = module.params.get("tenant_id")
    tenant_name = module.params.get("tenant_name")
    site_name = module.params.get("site_name")
    resource = module.params.get("resource")
    if resource is None:
        # Office 365 SharePoint Online 	00000003-0000-0ff1-ce00-000000000000
        resource = "00000003-0000-0ff1-ce00-000000000000/{}.sharepoint.com@{}".format(
            tenant_name, tenant_id
        )
    grant_type = module.params.get("grant_type")

    # Payload for token
    payload = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": resource,
    }

    # Auth url for token
    url_get_token = (
        "https://accounts.accesscontrol.windows.net/{}/tokens/oAuth/2".format(tenant_id)
    )

    response_token = requests.get(url_get_token, data=payload)

    if response_token.ok:
        token = json.loads(response_token.text)["access_token"]

        # headers
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json;odata=verbose",
            "Accept": "application/json;odata=verbose",
        }

        if method == "put":
            local_file_fullpath = os.path.join(local_file_path, local_file_name)
            try:
                # https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest#working-with-files-by-using-rest
                with open(local_file_fullpath, "rb") as file:

                    url = "https://{}.sharepoint.com/sites/{}".format(
                        tenant_name, site_name
                    )
                    command = "_api/web/GetFolderByServerRelativeURL('/sites/{}/{}')/Files/add(url='{}',overwrite=true)".format(
                        site_name, remote_file_path, remote_file_name
                    )

                    response = requests.post(
                        "{}/{}".format(url, command), headers=headers, data=file.read()
                    )

                if response.ok:
                    module.exit_json(
                        changed=True,
                        response=response.json(),
                        code=response.status_code,
                        # headers=headers,
                    )
                else:
                    module.fail_json(
                        msg="Something went wrong...",
                        response=response.json(),
                        code=response.status_code,
                        # headers=headers,
                    )

            except FileNotFoundError as e:
                module.fail_json(
                    msg="The file {} is missing.".format(local_file_fullpath)
                )

        if method == "get" or method == "metadata":
            url = "https://{}.sharepoint.com/sites/{}".format(tenant_name, site_name)
            command = (
                "/_api/web/GetFileByServerRelativeUrl('/sites/{}/{}/{}')/{}".format(
                    site_name, remote_file_path, remote_file_name, ODATA_SELECTORS[method]
                )
            )
            response = requests.get("{}/{}".format(url, command), headers=headers)
            if response.ok:
                content = response.content
                try:
                    if method == "get":
                        local_file_fullpath = os.path.join(local_file_path, local_file_name)
                        with open(local_file_fullpath, "wb") as file:
                            file.write(content)

                        module.exit_json(
                            changed=True,
                            code=response.status_code
                        )
                    elif method == "metadata":
                        module.exit_json(
                            changed=True,
                            code=response.status_code,
                            metadata=response.content
                        )
                except FileNotFoundError as e:
                    module.fail_json(
                        msg="The file {} is missing.".format(local_file_fullpath)
                    )
            else:
                module.fail_json(
                    msg="Something went wrong...",
                    response=response.json(),
                    code=response.status_code,
                    # headers=headers,
                )

        if method == "delete":
            headers["X-HTTP-Method"] = "DELETE"

            url = "https://{}.sharepoint.com/sites/{}".format(tenant_name, site_name)
            command = "/_api/web/GetFileByServerRelativeUrl('/sites/{}/{}/{}')".format(
                site_name, remote_file_path, remote_file_name
            )

            response = requests.post("{}/{}".format(url, command), headers=headers)
            if response.ok:
                module.exit_json(
                    changed=True,
                    code=response.status_code,
                    # headers=headers,
                )
            else:
                module.fail_json(
                    msg="Something went wrong...",
                    response=response.json(),
                    code=response.status_code,
                    # headers=headers,
                )
        
        if method == "list":
            headers["Accept"] = "application/json;odata=nometadata"
            url = "https://{}.sharepoint.com/sites/{}".format(tenant_name, site_name)

            result = []
            for kind in ["files", "folders"]:
                command = (
                    "/_api/web/GetFolderByServerRelativeUrl('{}')/{}".format(
                        remote_file_path, kind
                    )
                )

                response = requests.get("{}/{}".format(url, command), headers=headers)
                if response.ok:
                    for k in response.json()["value"]:
                        result.append(
                            {
                                "Kind": kind,
                                "Name": k["Name"],
                                "ServerRelativeUrl": k["ServerRelativeUrl"],
                                "TimeCreated": k["TimeCreated"],
                                "TimeLastModified": k["TimeLastModified"],
                            }
                        )

                else:
                    module.fail_json(
                        msg="Something went wrong...",
                        response=response.json(),
                        code=response.status_code,
                        command=command,
                    )

            module.exit_json(
                changed=True,
                code=response.status_code,
                command=command,
                listing=result,
            )

        if method == "mkdir":

            url = "https://{}.sharepoint.com/sites/{}".format(tenant_name, site_name)
            command = "/_api/web/folders"
            data = dict()
            data["__metadata"] = {"type": "SP.Folder"}
            data["ServerRelativeUrl"] = "/sites/{}{}".format(
                site_name, remote_file_path
            )

            response = requests.post(
                "{}/{}".format(url, command), headers=headers, data=json.dumps(data)
            )
            if response.ok:
                module.exit_json(
                    changed=True,
                    code=response.status_code,
                    # headers=headers,
                )
            else:
                module.fail_json(
                    msg="Something went wrong...",
                    response=response.json(),
                    data=data,
                    code=response.status_code,
                    # headers=headers,
                )

        if method == "rmdir":
            headers["X-HTTP-Method"] = "DELETE"

            url = "https://{}.sharepoint.com/sites/{}".format(tenant_name, site_name)
            command = "/_api/web/GetFolderByServerRelativeUrl('/sites/{}/{}')".format(
                site_name, remote_file_path
            )

            response = requests.post("{}/{}".format(url, command), headers=headers)
            if response.ok:
                module.exit_json(
                    changed=True,
                    code=response.status_code,
                    # headers=headers,
                )
            else:
                module.fail_json(
                    msg="Something went wrong...",
                    response=response.json(),
                    data=data,
                    code=response.status_code,
                    # headers=headers,
                )

    else:
        module.fail_json(
            msg="The OAuth 2.0 authorization failed (code: {})".format(
                response_token.status_code
            ),
            response=response_token.text,
        )


if __name__ == "__main__":
    main()
