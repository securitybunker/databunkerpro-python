"""
DatabunkerPro API Client
Main implementation of the DatabunkerPro API client.
"""

import json
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
            result = response.json()

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
            data.update(options)
        return self._make_request("UserCreate", "POST", data, request_metadata)

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
