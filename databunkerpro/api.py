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

    # User Management
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

    def patch_user(
        self,
        mode: str,
        identity: str,
        patch: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Patch a user record with specific changes.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            patch (Dict[str, Any]): The patch data to apply
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserPatch",
            "POST",
            {"mode": mode, "identity": identity, "patch": patch},
            request_metadata,
        )

    def request_user_patch(
        self,
        mode: str,
        identity: str,
        patch: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request a user patch operation.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            patch (Dict[str, Any]): The patch data to apply
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserPatchRequest",
            "POST",
            {"mode": mode, "identity": identity, "patch": patch},
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

    # User Authentication
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

    def create_captcha(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a captcha for user verification.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("CaptchaCreate", "POST", None, request_metadata)

    # Create user API Access Token
    def create_x_token(
        self,
        mode: str,
        identity: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates an access token for a user.

        Args:
            mode (str): User identification mode (e.g., 'email', 'phone', 'token')
            identity (str): User's identifier corresponding to the mode
            options (Dict[str, Any], optional): Optional parameters for token creation
                - tokentype (str): Type of token (e.g., 'access', 'refresh')
                - finaltime (str): Absolute expiration time for the token
                - slidingtime (str): Sliding time period for the token
            request_metadata (Dict[str, Any], optional): Optional request metadata

        Returns:
            Dict[str, Any]: The created token information
        """
        data = {"mode": mode, "identity": identity}
        if options:
            data.update(options)
        return self._make_request("XTokenCreate", "POST", data, request_metadata)

    # User Request Management
    def get_user_request(
        self, request_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a specific user request by UUID.

        Args:
            request_uuid (str): UUID of the request to retrieve
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserRequestGet", "POST", {"requestuuid": request_uuid}, request_metadata
        )

    def list_user_requests(
        self,
        mode: str,
        identity: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List user requests for a specific user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "UserRequestListUserRequests",
            "POST",
            {"mode": mode, "identity": identity, "offset": offset, "limit": limit},
            request_metadata,
        )

    def cancel_user_request(
        self,
        request_uuid: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Cancel a user request.

        Args:
            request_uuid (str): UUID of the request to cancel
            options (Dict[str, Any], optional): Optional parameters for cancellation
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"requestuuid": request_uuid}
        if options:
            data.update(options)
        return self._make_request("UserRequestCancel", "POST", data, request_metadata)

    def approve_user_request(
        self,
        request_uuid: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Approve a user request.

        Args:
            request_uuid (str): The UUID of the request to approve
            options (Dict[str, Any], optional): Optional parameters (only 'reason' is used)
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"requestuuid": request_uuid}
        if options and "reason" in options:
            data["reason"] = options["reason"]
        return self._make_request("UserRequestApprove", "POST", data, request_metadata)

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

    # Legal Basis Management
    def create_legal_basis(
        self,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a legal basis for data processing.

        Args:
            options (Dict[str, Any]): The legal basis options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "brief": options.get("brief"),
            "status": options.get("status"),
            "module": options.get("module"),
            "fulldesc": options.get("fulldesc"),
            "shortdesc": options.get("shortdesc"),
            "basistype": options.get("basistype"),
            "requiredmsg": options.get("requiredmsg"),
            "requiredflag": options.get("requiredflag"),
        }
        return self._make_request("LegalBasisCreate", "POST", data, request_metadata)

    def update_legal_basis(
        self,
        brief: str,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing legal basis.

        Args:
            brief (str): Unique identifier for the legal basis
            options (Dict[str, Any]): The legal basis update options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"brief": brief, **options}
        return self._make_request("LegalBasisUpdate", "POST", data, request_metadata)

    def delete_legal_basis(
        self, brief: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a legal basis.

        Args:
            brief (str): Unique identifier for the legal basis to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "LegalBasisDelete", "POST", {"brief": brief}, request_metadata
        )

    def list_agreements(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all agreements.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "LegalBasisListAgreements", "POST", None, request_metadata
        )

    # Agreement Management
    def accept_agreement(
        self,
        mode: str,
        identity: str,
        brief: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Accept an agreement for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            brief (str): The brief identifier of the agreement
            options (Dict[str, Any], optional): Additional options for agreement acceptance
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "mode": mode,
            "identity": identity,
            "brief": brief,
            "agreementmethod": options.get("agreementmethod") if options else None,
            "lastmodifiedby": options.get("lastmodifiedby") if options else None,
            "referencecode": options.get("referencecode") if options else None,
            "starttime": options.get("starttime") if options else None,
            "finaltime": options.get("finaltime") if options else None,
            "status": options.get("status") if options else None,
        }
        return self._make_request("AgreementAccept", "POST", data, request_metadata)

    def get_user_agreement(
        self,
        mode: str,
        identity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get a specific agreement for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            brief (str): Unique identifier of the legal basis/agreement
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AgreementGet",
            "POST",
            {"mode": mode, "identity": identity, "brief": brief},
            request_metadata,
        )

    def list_user_agreements(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List all agreements for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AgreementListUserAgreements",
            "POST",
            {"mode": mode, "identity": identity},
            request_metadata,
        )

    def cancel_agreement(
        self,
        mode: str,
        identity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Cancel an agreement for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            brief (str): Unique identifier of the legal basis/agreement to cancel
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AgreementCancel",
            "POST",
            {"mode": mode, "identity": identity, "brief": brief},
            request_metadata,
        )

    def request_agreement_cancellation(
        self,
        mode: str,
        identity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request cancellation of an agreement for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            brief (str): Unique identifier of the legal basis/agreement to cancel
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AgreementCancelRequest",
            "POST",
            {"mode": mode, "identity": identity, "brief": brief},
            request_metadata,
        )

    def revoke_all_agreements(
        self, brief: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Revoke all agreements for a specific legal basis.

        Args:
            brief (str): Unique identifier of the legal basis
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AgreementRevokeAll", "POST", {"brief": brief}, request_metadata
        )

    # Group Management
    def create_group(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new group.

        Args:
            options (Dict[str, Any], optional): Group creation options
                - groupname (str): The name of the group
                - groupdesc (str, optional): Description of the group
                - grouptype (str, optional): Type of the group
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "groupname": options.get("groupname") if options else None,
            "groupdesc": options.get("groupdesc") if options else None,
            "grouptype": options.get("grouptype") if options else None,
        }
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
        group_id: Union[str, int],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update group information.

        Args:
            group_id (Union[str, int]): The ID or name of the group
            options (Dict[str, Any], optional): Group update options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {}
        if isinstance(group_id, int) or str(group_id).isdigit():
            data["groupid"] = group_id
        else:
            data["groupname"] = group_id
        if options:
            data.update(options)
        return self._make_request("GroupUpdate", "POST", data, request_metadata)

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
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new tenant.

        Args:
            options (Dict[str, Any]): Tenant creation options
                - tenantname (str): Name of the tenant
                - tenantorg (str): Organization name
                - email (str): Email address for tenant contact
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "tenantname": options.get("tenantname"),
            "tenantorg": options.get("tenantorg"),
            "email": options.get("email"),
        }
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
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update tenant information.

        Args:
            tenant_id (str): The ID of the tenant to update
            options (Dict[str, Any]): Tenant update options
                - tenantname (str): New name of the tenant
                - tenantorg (str): New organization name
                - email (str): New email address for tenant admin
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"tenantid": tenant_id, **options}
        return self._make_request("TenantUpdate", "POST", data, request_metadata)

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
        self,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List all tenants with pagination.

        Args:
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "TenantListTenants",
            "POST",
            {"offset": offset, "limit": limit},
            request_metadata,
        )

    # Role Management
    def create_role(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new role.

        Args:
            options (Dict[str, Any], optional): Role creation options
                - rolename (str): The name of the role
                - roledesc (str, optional): Description of the role
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "rolename": options.get("rolename") if options else None,
            "roledesc": options.get("roledesc") if options else None,
        }
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
        role_id: Union[str, int],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update role information.

        Args:
            role_id (Union[str, int]): The ID or name of the role
            options (Dict[str, Any], optional): Role update options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {}
        if isinstance(role_id, int) or str(role_id).isdigit():
            data["roleid"] = role_id
        else:
            data["rolename"] = role_id
        if options:
            data.update(options)
        return self._make_request("RoleUpdate", "POST", data, request_metadata)

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
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new policy.

        Args:
            options (Dict[str, Any], optional): Policy creation options
                - policyname (str): The name of the policy
                - policydesc (str, optional): Description of the policy
                - policy (Dict[str, Any]): The policy configuration
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "policyname": options.get("policyname") if options else None,
            "policydesc": options.get("policydesc") if options else None,
            "policy": options.get("policy") if options else None,
        }
        return self._make_request("PolicyCreate", "POST", data, request_metadata)

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
        policy_id: Union[str, int],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update policy information.

        Args:
            policy_id (Union[str, int]): The ID or name of the policy
            options (Dict[str, Any], optional): Policy update options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {}
        if isinstance(policy_id, int) or str(policy_id).isdigit():
            data["policyid"] = policy_id
        else:
            data["policyname"] = policy_id
        if options:
            data.update(options)
        return self._make_request("PolicyUpdate", "POST", data, request_metadata)

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
        List all policies with enhanced information.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "PolicyListAllPolicies", "POST", None, request_metadata
        )

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

    # Token Management
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
        mode: str,
        identity: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a shared record for a user.

        Args:
            mode (str): User identification mode (e.g., 'email', 'phone', 'token')
            identity (str): User's identifier corresponding to the mode
            options (Dict[str, Any], optional): Optional parameters for shared record creation
                - fields (str): A string containing names of fields to share separated by commas
                - partner (str): It is used as a reference to partner name. It is not enforced.
                - appname (str): If defined, shows fields from the user app record instead user profile
                - finaltime (str): Expiration time for the shared record
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The created shared record information

        Example:
            # Create a shared record with specific fields
            shared_record = await api.create_shared_record('email', 'user@example.com', {
                'fields': 'name,email',
                'partner': 'partner-org',
                'appname': 'myapp',
                'finaltime': '100d'
            });
        """
        data = {
            "mode": mode,
            "identity": identity,
            "fields": options.get("fields") if options else None,
            "partner": options.get("partner") if options else None,
            "appname": options.get("appname") if options else None,
            "finaltime": options.get("finaltime") if options else None,
        }
        return self._make_request("SharedRecordCreate", "POST", data, request_metadata)

    def get_shared_record(
        self, record_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gets a shared record by its UUID.

        Args:
            record_uuid (str): UUID of the shared record to retrieve
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The shared record information

        Example:
            # Get a shared record by UUID
            shared_record = await api.get_shared_record('123e4567-e89b-12d3-a456-426614174000');
        """
        return self._make_request(
            "SharedRecordGet", "POST", {"recorduuid": record_uuid}, request_metadata
        )

    def update_shared_record(
        self,
        record_uuid: str,
        record_data: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update shared record information.

        Args:
            record_uuid (str): The UUID of the record
            record_data (Dict[str, Any]): The updated record data
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SharedRecordUpdate",
            "POST",
            {"recorduuid": record_uuid, "data": record_data},
            request_metadata,
        )

    def delete_shared_record(
        self, record_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a shared record.

        Args:
            record_uuid (str): The UUID of the record to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SharedRecordDelete", "POST", {"recorduuid": record_uuid}, request_metadata
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

    # Connector Management
    def list_supported_connectors(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all supported connector types.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ConnectorListSupportedConnectors", "POST", None, request_metadata
        )

    def list_connectors(
        self,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List connectors with pagination.

        Args:
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"offset": offset, "limit": limit}
        return self._make_request(
            "ConnectorListConnectors", "POST", data, request_metadata
        )

    def create_connector(
        self,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new database connector with the specified configuration.

        Args:
            options (Dict[str, Any]): The connector configuration options
                - connectorname (str): Name of the connector (e.g., "MySQL Production")
                - connectortype (str): Type of the connector (e.g., 'mysql', 'postgresql', 'mongodb')
                - apikey (str): API key for authentication with the database
                - username (str, optional): Username for database connection
                - connectordesc (str, optional): Description of the connector's purpose
                - dbhost (str, optional): Database host address (e.g., "db.example.com")
                - dbport (int, optional): Database port number (e.g., 3306 for MySQL)
                - dbname (str, optional): Name of the database to connect to
                - tablename (str, optional): Specific table name if applicable
                - status (str, optional): Status of the connector (e.g., 'active', 'inactive')
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The created connector details
        """
        data = {
            "connectorname": options.get("connectorname"),
            "connectortype": options.get("connectortype"),
            "connectordesc": options.get("connectordesc"),
            "username": options.get("username"),
            "apikey": options.get("apikey"),
            "dbhost": options.get("dbhost"),
            "dbport": options.get("dbport"),
            "dbname": options.get("dbname"),
            "tablename": options.get("tablename"),
            "status": options.get("status"),
        }
        return self._make_request("ConnectorCreate", "POST", data, request_metadata)

    def update_connector(
        self,
        connector_id: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing connector.

        Args:
            connector_id (Union[str, int]): The ID of the connector to update
            options (Dict[str, Any]): The connector update options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"connectorid": connector_id}
        data.update(options)
        return self._make_request("ConnectorUpdate", "POST", data, request_metadata)

    def validate_connector_connectivity(
        self,
        connector_id: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate connector connectivity.

        Args:
            connector_id (Union[str, int]): The ID of the connector
            options (Dict[str, Any]): The connector configuration options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "connectortype": options.get("connectortype"),
            "connectordesc": options.get("connectordesc"),
            "username": options.get("username"),
            "apikey": options.get("apikey"),
            "dbhost": options.get("dbhost"),
            "dbport": options.get("dbport"),
            "dbname": options.get("dbname"),
            "tablename": options.get("tablename"),
            "status": options.get("status"),
        }
        if isinstance(connector_id, int) or str(connector_id).isdigit():
            data["connectorid"] = connector_id
            data["connectorname"] = options.get("connectorname")
        else:
            data["connectorname"] = connector_id
        return self._make_request(
            "ConnectorValidateConnectivity", "POST", data, request_metadata
        )

    def delete_connector(
        self,
        connector_id: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delete a connector.

        Args:
            connector_id (Union[str, int]): The ID or name of the connector to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {}
        if isinstance(connector_id, int) or str(connector_id).isdigit():
            data["connectorid"] = connector_id
        else:
            data["connectorname"] = connector_id
        return self._make_request("ConnectorDelete", "POST", data, request_metadata)

    def get_table_metadata(
        self,
        connector_id: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get table metadata for a connector.

        Args:
            connector_id (Union[str, int]): The ID of the connector
            options (Dict[str, Any]): The connector configuration options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "connectortype": options.get("connectortype"),
            "connectordesc": options.get("connectordesc"),
            "username": options.get("username"),
            "apikey": options.get("apikey"),
            "dbhost": options.get("dbhost"),
            "dbport": options.get("dbport"),
            "dbname": options.get("dbname"),
            "tablename": options.get("tablename"),
            "status": options.get("status"),
        }
        if isinstance(connector_id, int) or str(connector_id).isdigit():
            data["connectorid"] = connector_id
            data["connectorname"] = options.get("connectorname")
        else:
            data["connectorname"] = connector_id
        return self._make_request(
            "ConnectorGetTableMetaData", "POST", data, request_metadata
        )

    def connector_get_user_data(
        self,
        mode: str,
        identity: str,
        connector_id: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get user data from a connector.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            connector_id (Union[str, int]): The ID of the connector
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"mode": mode, "identity": identity}
        if isinstance(connector_id, int) or str(connector_id).isdigit():
            data["connectorid"] = connector_id
        else:
            data["connectorname"] = connector_id
        return self._make_request(
            "ConnectorGetUserData", "POST", data, request_metadata
        )

    def connector_get_user_extra_data(
        self,
        mode: str,
        identity: str,
        connector_id: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get user extra data from a connector.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            connector_id (Union[str, int]): The ID of the connector
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"mode": mode, "identity": identity}
        if isinstance(connector_id, int) or str(connector_id).isdigit():
            data["connectorid"] = connector_id
        else:
            data["connectorname"] = connector_id
        return self._make_request(
            "ConnectorGetUserExtraData", "POST", data, request_metadata
        )

    def connector_delete_user(
        self,
        mode: str,
        identity: str,
        connector_id: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delete user data from a connector.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            connector_id (Union[str, int]): The ID of the connector
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"mode": mode, "identity": identity}
        if isinstance(connector_id, int) or str(connector_id).isdigit():
            data["connectorid"] = connector_id
        else:
            data["connectorname"] = connector_id
        return self._make_request("ConnectorDeleteUser", "POST", data, request_metadata)

    # Processing Activity Management
    def list_processing_activities(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all processing activities.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ProcessingActivityListActivities", "POST", None, request_metadata
        )

    def create_processing_activity(
        self,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new processing activity.

        Args:
            options (Dict[str, Any]): The processing activity options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {
            "activity": options.get("activity"),
            "title": options.get("title"),
            "script": options.get("script"),
            "fulldesc": options.get("fulldesc"),
            "applicableto": options.get("applicableto"),
        }
        return self._make_request(
            "ProcessingActivityCreate", "POST", data, request_metadata
        )

    def update_processing_activity(
        self,
        activity: str,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing processing activity.

        Args:
            activity (str): Current activity identifier
            options (Dict[str, Any]): The processing activity update options
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data = {"activity": activity, **options}
        return self._make_request(
            "ProcessingActivityUpdate", "POST", data, request_metadata
        )

    def delete_processing_activity(
        self, activity: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete a processing activity.

        Args:
            activity (str): Activity identifier to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ProcessingActivityDelete", "POST", {"activity": activity}, request_metadata
        )

    def link_processing_activity_to_legal_basis(
        self,
        activity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Link a processing activity to a legal basis.

        Args:
            activity (str): Activity identifier
            brief (str): Legal basis brief identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ProcessingActivityLinkLegalBasis",
            "POST",
            {"activity": activity, "brief": brief},
            request_metadata,
        )

    def unlink_processing_activity_from_legal_basis(
        self,
        activity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Unlink a processing activity from a legal basis.

        Args:
            activity (str): Activity identifier
            brief (str): Legal basis brief identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "ProcessingActivityUnlinkLegalBasis",
            "POST",
            {"activity": activity, "brief": brief},
            request_metadata,
        )

    # Enhanced Group Management
    def list_all_groups(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all groups in the system.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("GroupListAllGroups", "POST", None, request_metadata)

    def list_user_groups(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List groups for a specific user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "GroupListUserGroups",
            "POST",
            {"mode": mode, "identity": identity},
            request_metadata,
        )

    def remove_user_from_group(
        self,
        mode: str,
        identity: str,
        group_id: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Remove a user from a group.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            group_id (str): The group ID
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "GroupDeleteUser",
            "POST",
            {"mode": mode, "identity": identity, "groupid": group_id},
            request_metadata,
        )

    def add_user_to_group(
        self,
        mode: str,
        identity: str,
        group_name: Union[str, int],
        role_name: Optional[Union[str, int]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a user to a group with an optional role.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            group_name (Union[str, int]): Group name or ID to add the user to
            role_name (Union[str, int], optional): Optional role name or ID to assign to the user in the group
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data: Dict[str, Any] = {"mode": mode, "identity": identity}

        # Check if group_name is an integer (group ID) or string (group name)
        if isinstance(group_name, int) or str(group_name).isdigit():
            data["groupid"] = group_name
        else:
            data["groupname"] = str(group_name)

        if role_name is not None:
            # Check if role_name is an integer (role ID) or string (role name)
            if isinstance(role_name, int) or str(role_name).isdigit():
                data["roleid"] = role_name
            else:
                data["rolename"] = str(role_name)

        return self._make_request("GroupAddUser", "POST", data, request_metadata)

    # Enhanced Audit Management
    def list_user_audit_events(
        self,
        mode: str,
        identity: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List audit events for a specific user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AuditListUserEvents",
            "POST",
            {"mode": mode, "identity": identity, "offset": offset, "limit": limit},
            request_metadata,
        )

    def get_audit_event(
        self, audit_event_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a specific audit event by UUID.

        Args:
            audit_event_uuid (str): UUID of the audit event to retrieve
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "AuditGetEvent",
            "POST",
            {"auditeventuuid": audit_event_uuid},
            request_metadata,
        )

    # Enhanced Role Management
    def link_policy(
        self,
        role_name: str,
        policy_name: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Link a policy to a role.

        Args:
            role_name (str): Name of the role
            policy_name (str): Name of the policy to link
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "RoleLinkPolicy",
            "POST",
            {"rolename": role_name, "policyname": policy_name},
            request_metadata,
        )

    # Bulk Operations
    def bulk_list_unlock(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a bulk list unlock operation.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("BulkListUnlock", "POST", None, request_metadata)

    def bulk_list_users(
        self,
        unlock_uuid: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List users in a bulk operation.

        Args:
            unlock_uuid (str): UUID of the unlock operation
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "BulkListUsers",
            "POST",
            {"unlockuuid": unlock_uuid, "offset": offset, "limit": limit},
            request_metadata,
        )

    def bulk_list_group_users(
        self,
        unlock_uuid: str,
        group_name: Union[str, int],
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List users in a group for a bulk operation.

        Args:
            unlock_uuid (str): UUID of the unlock operation
            group_name (Union[str, int]): Group name or ID
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        data: Dict[str, Any] = {
            "unlockuuid": unlock_uuid,
            "offset": offset,
            "limit": limit,
        }
        if isinstance(group_name, int) or str(group_name).isdigit():
            data["groupid"] = group_name
        else:
            data["groupname"] = str(group_name)
        return self._make_request("BulkListGroupUsers", "POST", data, request_metadata)

    def bulk_list_user_requests(
        self,
        unlock_uuid: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List user requests in a bulk operation.

        Args:
            unlock_uuid (str): UUID of the unlock operation
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "BulkListUserRequests",
            "POST",
            {"unlockuuid": unlock_uuid, "offset": offset, "limit": limit},
            request_metadata,
        )

    def bulk_list_audit_events(
        self,
        unlock_uuid: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List audit events in a bulk operation.

        Args:
            unlock_uuid (str): UUID of the unlock operation
            offset (int, optional): Offset for pagination. Defaults to 0
            limit (int, optional): Limit for pagination. Defaults to 10
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "BulkListAuditEvents",
            "POST",
            {"unlockuuid": unlock_uuid, "offset": offset, "limit": limit},
            request_metadata,
        )

    def bulk_list_tokens(
        self,
        unlock_uuid: str,
        tokens: List[str],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List tokens in a bulk operation.

        Args:
            unlock_uuid (str): UUID of the unlock operation
            tokens (List[str]): List of tokens to retrieve
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "BulkListTokens",
            "POST",
            {"unlockuuid": unlock_uuid, "tokens": tokens},
            request_metadata,
        )

    def bulk_delete_tokens(
        self,
        unlock_uuid: str,
        tokens: List[str],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delete tokens in a bulk operation.

        Args:
            unlock_uuid (str): UUID of the unlock operation
            tokens (List[str]): List of tokens to delete
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "BulkDeleteTokens",
            "POST",
            {"unlockuuid": unlock_uuid, "tokens": tokens},
            request_metadata,
        )

    # Enhanced System Configuration
    def get_ui_conf(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get UI configuration.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("TenantGetUIConf", "POST", None, request_metadata)

    def get_tenant_conf(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get tenant configuration.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request("TenantGetConf", "POST", None, request_metadata)

    def get_user_html_report(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get HTML report for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SystemGetUserHTMLReport",
            "POST",
            {"mode": mode, "identity": identity},
            request_metadata,
        )

    def get_user_report(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get report for a user.

        Args:
            mode (str): The identification mode (e.g., 'email', 'phone', 'token')
            identity (str): The user's identifier
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The API response
        """
        return self._make_request(
            "SystemGetUserReport",
            "POST",
            {"mode": mode, "identity": identity},
            request_metadata,
        )

    # Captcha Management

    # System Metrics
    def get_system_stats(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gets system statistics.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: System statistics

        Response format:
        {
          "status": "ok",
          "stats": {
            "numusers": 123,      // Total number of users in the system
            "numtenants": 123,    // Total number of tenants
            "numtokens": 123,     // Total number of tokens
            "numsessions": 123    // Total number of active sessions
          }
        }
        """
        return self._make_request(
            "SystemGetSystemStats", "POST", None, request_metadata
        )

    def get_system_metrics(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get system metrics in Prometheus format.

        Args:
            request_metadata (Dict[str, Any], optional): Additional metadata for the request

        Returns:
            Dict[str, Any]: The parsed metrics
        """
        try:
            response = requests.get(f"{self.base_url}/metrics")
            metrics_text = response.text
            return self.parse_prometheus_metrics(metrics_text)
        except Exception as e:
            return {"status": "error", "message": f"Error getting metrics: {str(e)}"}

    def _parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """
        Parse Prometheus metrics text into a dictionary.

        Args:
            metrics_text (str): Raw metrics text in Prometheus format

        Returns:
            Dict[str, Any]: Parsed metrics
        """
        metrics = {}
        lines = metrics_text.split("\n")

        for line in lines:
            # Skip comments and empty lines
            if line.startswith("#") or not line.strip():
                continue

            # Parse metric line
            import re

            match = re.match(r"^([a-zA-Z0-9_]+)(?:{([^}]+)})?\s+([0-9.]+)$", line)
            if match:
                name, labels, value = match.groups()
                metric_key = f"{name}{{{labels}}}" if labels else name
                metrics[metric_key] = float(value)

        return metrics

    def parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """
        Parse Prometheus metrics text into a dictionary.

        Args:
            metrics_text (str): Raw metrics text in Prometheus format

        Returns:
            Dict[str, Any]: Parsed metrics
        """
        return self._parse_prometheus_metrics(metrics_text)
