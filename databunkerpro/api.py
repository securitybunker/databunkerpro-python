"""
DatabunkerPro API Client
Main implementation of the DatabunkerPro API client.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests


class DatabunkerproAPI:
    """Main client class for interacting with the DatabunkerPro API."""

    def __init__(
        self, base_url: str, x_bunker_token: str = "", x_bunker_tenant: str = ""
    ):
        """
        Initialize the DatabunkerPro API client.

        Args:
            base_url (str): The base URL of the DatabunkerPro API
            x_bunker_token (str, optional): The X-Bunker-Token for authentication
            x_bunker_tenant (str, optional): The X-Bunker-Tenant identifier
        """
        self.base_url = base_url.rstrip("/")
        self.x_bunker_token = x_bunker_token
        self.x_bunker_tenant = x_bunker_tenant

    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the DatabunkerPro API.

        Args:
            endpoint (str): The API endpoint to call
            method (str, optional): The HTTP method to use. Defaults to "POST"
            data (Dict[str, Any], optional): The data to send in the request body
            request_metadata (Dict[str, Any], optional): Additional metadata to include in the request

        Returns:
            Dict[str, Any]: The API response

        Raises:
            Exception: If the API request fails
        """
        headers = {"Content-Type": "application/json"}

        if self.x_bunker_token:
            headers["X-Bunker-Token"] = self.x_bunker_token
        if self.x_bunker_tenant:
            headers["X-Bunker-Tenant"] = self.x_bunker_tenant

        url = f"{self.base_url}/v2/{endpoint}"

        if data or request_metadata:
            body_data = data.copy() if data else {}
            if request_metadata:
                body_data["request_metadata"] = request_metadata
            body = json.dumps(body_data)
        else:
            body = None

        try:
            response = requests.request(method, url, headers=headers, data=body)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()

            if not response.ok:
                if result.get("status"):
                    return result
                else:
                    return {
                        "status": "error",
                        "message": result.get("message", "API request failed"),
                    }

            return result
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Error making request: {str(e)}"}

    def raw_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Make a raw request to the DatabunkerPro API and return the response content.

        Args:
            endpoint (str): The API endpoint to call
            method (str, optional): The HTTP method to use. Defaults to "POST"
            data (Dict[str, Any], optional): The data to send in the request body
            request_metadata (Dict[str, Any], optional): Additional metadata to include in the request

        Returns:
            bytes: The raw response content
        """
        headers = {"Content-Type": "application/json"}

        if self.x_bunker_token:
            headers["X-Bunker-Token"] = self.x_bunker_token

        url = f"{self.base_url}/v2/{endpoint}"

        if data or request_metadata:
            body_data = data.copy() if data else {}
            if request_metadata:
                body_data["request_metadata"] = request_metadata
            body = json.dumps(body_data)
        else:
            body = None

        response = requests.request(method, url, headers=headers, data=body)
        return response.content

    def create_user(
        self,
        profile: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new user in DatabunkerPro.

        Args:
            profile (Dict[str, Any]): User profile data
            options (Dict[str, Any], optional): Additional options for user creation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"profile": profile}
        if options:
            if "groupname" in options:
                if str(options["groupname"]).isdigit():
                    data["groupid"] = options["groupname"]
                else:
                    data["groupname"] = options["groupname"]
            elif "groupid" in options:
                data["groupid"] = options["groupid"]

            if "rolename" in options:
                if str(options["rolename"]).isdigit():
                    data["roleid"] = options["rolename"]
                else:
                    data["rolename"] = options["rolename"]
            elif "roleid" in options:
                data["roleid"] = options["roleid"]

            if "slidingtime" in options:
                data["slidingtime"] = options["slidingtime"]
            if "finaltime" in options:
                data["finaltime"] = options["finaltime"]

        return self._make_request("UserCreate", "POST", data, request_metadata)

    def create_users_bulk(
        self,
        records: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create multiple users in bulk with their profiles and group information.

        Args:
            records (List[Dict[str, Any]]): List of user records to create
            options (Dict[str, Any], optional): Global options for all users
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "records": [
                {
                    "profile": record["profile"],
                    **(
                        {
                            (
                                "groupid"
                                if str(record.get("groupname", "")).isdigit()
                                else "groupname"
                            ): record["groupname"]
                        }
                        if "groupname" in record
                        else {}
                    ),
                    **({"groupid": record["groupid"]} if "groupid" in record else {}),
                    **(
                        {
                            (
                                "roleid"
                                if str(record.get("rolename", "")).isdigit()
                                else "rolename"
                            ): record["rolename"]
                        }
                        if "rolename" in record
                        else {}
                    ),
                    **({"roleid": record["roleid"]} if "roleid" in record else {}),
                }
                for record in records
            ]
        }

        if options:
            if "finaltime" in options:
                data["finaltime"] = options["finaltime"]
            if "slidingtime" in options:
                data["slidingtime"] = options["slidingtime"]

        return self._make_request("UserCreateBulk", "POST", data, request_metadata)

    def get_user(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get user information from DatabunkerPro.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserGet", "POST", {"mode": mode, "identity": identity}, request_metadata
        )

    def update_user(
        self,
        mode: str,
        identity: str,
        profile: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update user information in DatabunkerPro.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            profile (Dict[str, Any]): Updated user profile data
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserUpdate",
            "POST",
            {"mode": mode, "identity": identity, "profile": profile},
            request_metadata,
        )

    def delete_user(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delete a user from DatabunkerPro.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserDelete", "POST", {"mode": mode, "identity": identity}, request_metadata
        )

    def request_user_deletion(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request deletion of a user from DatabunkerPro.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserDeleteRequest",
            "POST",
            {"mode": mode, "identity": identity},
            request_metadata,
        )

    def request_user_update(
        self,
        mode: str,
        identity: str,
        profile: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request update of user information in DatabunkerPro.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            profile (Dict[str, Any]): Updated user profile data
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserUpdateRequest",
            "POST",
            {"mode": mode, "identity": identity, "profile": profile},
            request_metadata,
        )

    def prelogin_user(
        self,
        mode: str,
        identity: str,
        code: str,
        captchacode: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform pre-login operations for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            code (str): The verification code
            captchacode (str): The CAPTCHA code
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserPrelogin",
            "POST",
            {
                "mode": mode,
                "identity": identity,
                "code": code,
                "captchacode": captchacode,
            },
            request_metadata,
        )

    def login_user(
        self,
        mode: str,
        identity: str,
        smscode: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Log in a user with SMS verification.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            smscode (str): The SMS verification code
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserLogin",
            "POST",
            {"mode": mode, "identity": identity, "smscode": smscode},
            request_metadata,
        )

    # App Data Management
    def create_app_data(
        self,
        mode: str,
        identity: str,
        appname: str,
        data: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create application data for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            appname (str): The name of the application
            data (Dict[str, Any]): The application data to store
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AppdataCreate",
            "POST",
            {"mode": mode, "identity": identity, "appname": appname, "data": data},
            request_metadata,
        )

    def get_app_data(
        self,
        mode: str,
        identity: str,
        appname: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get application data for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            appname (str): The name of the application
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AppdataGet",
            "POST",
            {"mode": mode, "identity": identity, "appname": appname},
            request_metadata,
        )

    def update_app_data(
        self,
        mode: str,
        identity: str,
        appname: str,
        data: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update application data for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            appname (str): The name of the application
            data (Dict[str, Any]): The updated application data
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AppdataUpdate",
            "POST",
            {"mode": mode, "identity": identity, "appname": appname, "data": data},
            request_metadata,
        )

    def request_app_data_update(
        self,
        mode: str,
        identity: str,
        appname: str,
        data: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request update of application data for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            appname (str): The name of the application
            data (Dict[str, Any]): The updated application data
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AppdataUpdateRequest",
            "POST",
            {"mode": mode, "identity": identity, "appname": appname, "data": data},
            request_metadata,
        )

    def list_app_data_records(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List all application data records for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AppdataListUserAppNames",
            "POST",
            {"mode": mode, "identity": identity},
            request_metadata,
        )

    def list_app_names(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all application names in the system.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("AppdataListAppNames", "POST", None, request_metadata)

    def get_system_stats(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get system statistics from DatabunkerPro.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response containing system statistics
        """
        return self._make_request(
            "SystemGetSystemStats", "POST", None, request_metadata
        )

    def create_token(
        self,
        token_type: str,
        record: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a token for sensitive data.

        Args:
            token_type (str): Type of token (e.g., 'creditcard')
            record (str): The sensitive data to tokenize
            options (Dict[str, Any], optional): Additional options for token creation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"tokentype": token_type, "record": record}
        if options:
            data.update(options)
        return self._make_request("TokenCreate", "POST", data, request_metadata)

    def create_tokens_bulk(
        self,
        records: List[Dict[str, Any]],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create multiple tokens in bulk.

        Args:
            records (List[Dict[str, Any]]): List of token records to create
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TokenCreateBulk", "POST", {"records": records}, request_metadata
        )

    def delete_tokens_bulk(
        self,
        tokens: List[str],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delete multiple tokens in bulk.

        Args:
            tokens (List[str]): List of tokens to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TokenDeleteBulk", "POST", {"tokens": tokens}, request_metadata
        )

    def get_token(
        self, token: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get token information from DatabunkerPro.

        Args:
            token (str): The token to retrieve
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TokenGet", "POST", {"token": token}, request_metadata
        )

    def delete_token(
        self, token: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a token from DatabunkerPro.

        Args:
            token (str): The token to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TokenDelete", "POST", {"token": token}, request_metadata
        )

    # Agreement Management
    def create_legal_basis(
        self,
        mode: str,
        identity: str,
        legal_basis: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a legal basis for data processing.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            legal_basis (Dict[str, Any]): The legal basis information
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "LegalBasisCreate",
            "POST",
            {"mode": mode, "identity": identity, "legalbasis": legal_basis},
            request_metadata,
        )

    def accept_agreement(
        self,
        mode: str,
        identity: str,
        agreement_id: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Accept an agreement for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            agreement_id (str): The ID of the agreement to accept
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AgreementAccept",
            "POST",
            {"mode": mode, "identity": identity, "agreementid": agreement_id},
            request_metadata,
        )

    # Group Management
    def create_group(
        self,
        name: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new group.

        Args:
            name (str): The name of the group
            options (Dict[str, Any], optional): Additional options for group creation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"name": name}
        if options:
            data.update(options)
        return self._make_request("GroupCreate", "POST", data, request_metadata)

    def get_group(
        self, group_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get group information.

        Args:
            group_id (str): The ID of the group
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "GroupGet", "POST", {"groupid": group_id}, request_metadata
        )

    def update_group(
        self,
        group_id: str,
        name: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update group information.

        Args:
            group_id (str): The ID of the group
            name (str): The new name for the group
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "GroupUpdate", "POST", {"groupid": group_id, "name": name}, request_metadata
        )

    def delete_group(
        self, group_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a group.

        Args:
            group_id (str): The ID of the group to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "GroupDelete", "POST", {"groupid": group_id}, request_metadata
        )

    def list_groups(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all groups.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("GroupList", "POST", None, request_metadata)

    # Audit Management
    def get_audit_log(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get audit log entries.

        Args:
            options (Dict[str, Any], optional): Filtering options for the audit log
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("AuditGetLog", "POST", options, request_metadata)

    def get_audit_stats(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("AuditGetStats", "POST", None, request_metadata)

    # Tenant Management
    def create_tenant(
        self,
        name: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new tenant.

        Args:
            name (str): The name of the tenant
            options (Dict[str, Any], optional): Additional options for tenant creation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"name": name}
        if options:
            data.update(options)
        return self._make_request("TenantCreate", "POST", data, request_metadata)

    def get_tenant(
        self, tenant_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get tenant information.

        Args:
            tenant_id (str): The ID of the tenant
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TenantGet", "POST", {"tenantid": tenant_id}, request_metadata
        )

    def update_tenant(
        self,
        tenant_id: str,
        name: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update tenant information.

        Args:
            tenant_id (str): The ID of the tenant
            name (str): The new name for the tenant
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TenantUpdate",
            "POST",
            {"tenantid": tenant_id, "name": name},
            request_metadata,
        )

    def delete_tenant(
        self, tenant_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a tenant.

        Args:
            tenant_id (str): The ID of the tenant to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TenantDelete", "POST", {"tenantid": tenant_id}, request_metadata
        )

    def list_tenants(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all tenants.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("TenantList", "POST", None, request_metadata)

    # Role Management
    def create_role(
        self,
        name: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new role.

        Args:
            name (str): The name of the role
            options (Dict[str, Any], optional): Additional options for role creation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"name": name}
        if options:
            data.update(options)
        return self._make_request("RoleCreate", "POST", data, request_metadata)

    def get_role(
        self, role_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get role information.

        Args:
            role_id (str): The ID of the role
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "RoleGet", "POST", {"roleid": role_id}, request_metadata
        )

    def update_role(
        self,
        role_id: str,
        name: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update role information.

        Args:
            role_id (str): The ID of the role
            name (str): The new name for the role
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "RoleUpdate", "POST", {"roleid": role_id, "name": name}, request_metadata
        )

    def delete_role(
        self, role_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a role.

        Args:
            role_id (str): The ID of the role to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "RoleDelete", "POST", {"roleid": role_id}, request_metadata
        )

    def list_roles(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all roles.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("RoleList", "POST", None, request_metadata)

    # Policy Management
    def create_policy(
        self,
        name: str,
        policy: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new policy.

        Args:
            name (str): The name of the policy
            policy (Dict[str, Any]): The policy configuration
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "PolicyCreate", "POST", {"name": name, "policy": policy}, request_metadata
        )

    def get_policy(
        self, policy_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get policy information.

        Args:
            policy_id (str): The ID of the policy
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "PolicyGet", "POST", {"policyid": policy_id}, request_metadata
        )

    def update_policy(
        self,
        policy_id: str,
        name: str,
        policy: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update policy information.

        Args:
            policy_id (str): The ID of the policy
            name (str): The new name for the policy
            policy (Dict[str, Any]): The updated policy configuration
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "PolicyUpdate",
            "POST",
            {"policyid": policy_id, "name": name, "policy": policy},
            request_metadata,
        )

    def delete_policy(
        self, policy_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a policy.

        Args:
            policy_id (str): The ID of the policy to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "PolicyDelete", "POST", {"policyid": policy_id}, request_metadata
        )

    def list_policies(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all policies.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("PolicyList", "POST", None, request_metadata)

    # System Configuration
    def get_system_config(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get system configuration.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("SystemGetConfig", "POST", None, request_metadata)

    def update_system_config(
        self,
        config: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update system configuration.

        Args:
            config (Dict[str, Any]): The new system configuration
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SystemUpdateConfig", "POST", config, request_metadata
        )

    # User Request Management
    def get_user_requests(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get user requests.

        Args:
            options (Dict[str, Any], optional): Filtering options for the requests
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("UserRequestGet", "POST", options, request_metadata)

    def approve_user_request(
        self,
        request_id: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Approve a user request.

        Args:
            request_id (str): The ID of the request to approve
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserRequestApprove", "POST", {"requestid": request_id}, request_metadata
        )

    def reject_user_request(
        self,
        request_id: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Reject a user request.

        Args:
            request_id (str): The ID of the request to reject
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserRequestReject", "POST", {"requestid": request_id}, request_metadata
        )

    # Connector Management
    def create_connector(
        self,
        name: str,
        connector_type: str,
        config: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new connector.

        Args:
            name (str): The name of the connector
            connector_type (str): The type of connector
            config (Dict[str, Any]): The connector configuration
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ConnectorCreate",
            "POST",
            {"name": name, "type": connector_type, "config": config},
            request_metadata,
        )

    def get_connector(
        self, connector_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get connector information.

        Args:
            connector_id (str): The ID of the connector
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ConnectorGet", "POST", {"connectorid": connector_id}, request_metadata
        )

    def update_connector(
        self,
        connector_id: str,
        name: str,
        config: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update connector information.

        Args:
            connector_id (str): The ID of the connector
            name (str): The new name for the connector
            config (Dict[str, Any]): The updated connector configuration
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ConnectorUpdate",
            "POST",
            {"connectorid": connector_id, "name": name, "config": config},
            request_metadata,
        )

    def delete_connector(
        self, connector_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a connector.

        Args:
            connector_id (str): The ID of the connector to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ConnectorDelete", "POST", {"connectorid": connector_id}, request_metadata
        )

    def list_connectors(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all connectors.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("ConnectorList", "POST", None, request_metadata)

    # Session Management
    def create_session(
        self,
        mode: str,
        identity: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create or update a session (upsert operation).
        If a session already exists for the given user, it will be updated.
        Otherwise, a new session will be created.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            options (Dict[str, Any], optional): Additional options for session creation/update
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"mode": mode, "identity": identity}
        if options:
            data.update(options)
        return self._make_request("SessionUpsert", "POST", data, request_metadata)

    def get_session(
        self, session_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get session information.

        Args:
            session_id (str): The ID of the session
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SessionGet", "POST", {"sessionid": session_id}, request_metadata
        )

    def delete_session(
        self, session_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a session.

        Args:
            session_id (str): The ID of the session to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SessionDelete", "POST", {"sessionid": session_id}, request_metadata
        )

    def list_sessions(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List all sessions.

        Args:
            options (Dict[str, Any], optional): Filtering options for the sessions
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("SessionList", "POST", options, request_metadata)

    # Shared Record Management
    def create_shared_record(
        self,
        record_type: str,
        record_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new shared record.

        Args:
            record_type (str): The type of record
            record_data (Dict[str, Any]): The record data
            options (Dict[str, Any], optional): Additional options for record creation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"type": record_type, "data": record_data}
        if options:
            data.update(options)
        return self._make_request("SharedRecordCreate", "POST", data, request_metadata)

    def get_shared_record(
        self, record_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get shared record information.

        Args:
            record_id (str): The ID of the record
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SharedRecordGet", "POST", {"recordid": record_id}, request_metadata
        )

    def update_shared_record(
        self,
        record_id: str,
        record_data: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update shared record information.

        Args:
            record_id (str): The ID of the record
            record_data (Dict[str, Any]): The updated record data
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SharedRecordUpdate",
            "POST",
            {"recordid": record_id, "data": record_data},
            request_metadata,
        )

    def delete_shared_record(
        self, record_id: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a shared record.

        Args:
            record_id (str): The ID of the record to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SharedRecordDelete", "POST", {"recordid": record_id}, request_metadata
        )

    def list_shared_records(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List all shared records.

        Args:
            options (Dict[str, Any], optional): Filtering options for the records
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("SharedRecordList", "POST", options, request_metadata)
