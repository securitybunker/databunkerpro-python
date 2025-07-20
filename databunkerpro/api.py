"""DatabunkerPro API Client"""

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
        """Initialize the DatabunkerPro API client."""
        self.base_url = base_url.rstrip("/")
        self.x_bunker_token = x_bunker_token
        self.x_bunker_tenant = x_bunker_tenant

    def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the DatabunkerPro API."""
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
            response = requests.post(url, headers=headers, data=body)
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
        data: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Make a raw request to the DatabunkerPro API and return the response content."""
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
        response = requests.post(url, headers=headers, data=body)
        return response.content

    # User Management
    def create_user(
        self,
        profile: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new user in DatabunkerPro."""
        data = {"profile": profile}
        if options:
            # Handle groupname/groupid
            if "groupname" in options:
                if str(options["groupname"]).isdigit():
                    data["groupid"] = options["groupname"]
                else:
                    data["groupname"] = options["groupname"]
            elif "groupid" in options:
                data["groupid"] = options["groupid"]
            # Handle rolename/roleid
            if "rolename" in options:
                if str(options["rolename"]).isdigit():
                    data["roleid"] = options["rolename"]
                else:
                    data["rolename"] = options["rolename"]
            elif "roleid" in options:
                data["roleid"] = options["roleid"]
            # Handle time parameters
            if "slidingtime" in options:
                data["slidingtime"] = options["slidingtime"]
            if "finaltime" in options:
                data["finaltime"] = options["finaltime"]
        return self._make_request("UserCreate", data, request_metadata)

    def create_users_bulk(
        self,
        records: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create multiple users in bulk."""
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
        return self._make_request("UserCreateBulk", data, request_metadata)

    def get_user(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get user information from DatabunkerPro."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("UserGet", data, request_metadata)

    def update_user(
        self,
        mode: str,
        identity: str,
        profile: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update user information in DatabunkerPro."""
        data = {
            "mode": mode,
            "identity": identity,
            "profile": profile,
        }
        return self._make_request("UserUpdate", data, request_metadata)

    def request_user_update(
        self,
        mode: str,
        identity: str,
        profile: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Request update of user information in DatabunkerPro."""
        data = {
            "mode": mode,
            "identity": identity,
            "profile": profile,
        }
        return self._make_request("UserUpdateRequest", data, request_metadata)

    def patch_user(
        self,
        mode: str,
        identity: str,
        patch: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Patch a user record with specific changes."""
        data = {
            "mode": mode,
            "identity": identity,
            "patch": patch,
        }
        return self._make_request("UserPatch", data, request_metadata)

    def request_user_patch(
        self,
        mode: str,
        identity: str,
        patch: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Request a user patch operation."""
        data = {
            "mode": mode,
            "identity": identity,
            "patch": patch,
        }
        return self._make_request("UserPatchRequest", data, request_metadata)

    def delete_user(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete a user from DatabunkerPro."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("UserDelete", data, request_metadata)

    def request_user_deletion(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Request deletion of a user from DatabunkerPro."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("UserDeleteRequest", data, request_metadata)

    # User Authentication
    def prelogin_user(
        self,
        mode: str,
        identity: str,
        code: str,
        captchacode: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform pre-login operations for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "code": code,
            "captchacode": captchacode,
        }
        return self._make_request("UserPrelogin", data, request_metadata)

    def login_user(
        self,
        mode: str,
        identity: str,
        smscode: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log in a user with SMS verification."""
        data = {
            "mode": mode,
            "identity": identity,
            "smscode": smscode,
        }
        return self._make_request("UserLogin", data, request_metadata)

    def create_captcha(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a captcha for user verification."""
        return self._make_request("CaptchaCreate", None, request_metadata)

    def create_x_token(
        self,
        mode: str,
        identity: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Creates an access token for a user."""
        data = {"mode": mode, "identity": identity}
        if options:
            data.update(options)
        return self._make_request("XTokenCreate", data, request_metadata)

    # User Request Management
    def get_user_request(
        self, request_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a specific user request by UUID."""
        data = {
            "requestuuid": request_uuid,
        }
        return self._make_request("UserRequestGet", data, request_metadata)

    def list_user_requests(
        self,
        mode: str,
        identity: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List user requests for a specific user."""
        data = {
            "mode": mode,
            "identity": identity,
            "offset": offset,
            "limit": limit,
        }
        return self._make_request("UserRequestListUserRequests", data, request_metadata)

    def cancel_user_request(
        self,
        request_uuid: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Cancel a user request."""
        data = {"requestuuid": request_uuid}
        if options:
            data.update(options)
        return self._make_request("UserRequestCancel", data, request_metadata)

    def approve_user_request(
        self,
        request_uuid: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Approve a user request."""
        data = {"requestuuid": request_uuid}
        if options and "reason" in options:
            data["reason"] = options["reason"]
        return self._make_request("UserRequestApprove", data, request_metadata)

    # App Data Management
    def create_app_data(
        self,
        mode: str,
        identity: str,
        appname: str,
        appdata: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create application data for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "appname": appname,
            "appdata": appdata,
        }
        return self._make_request("AppdataCreate", data, request_metadata)

    def get_app_data(
        self,
        mode: str,
        identity: str,
        appname: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get application data for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "appname": appname,
        }
        return self._make_request("AppdataGet", data, request_metadata)

    def update_app_data(
        self,
        mode: str,
        identity: str,
        appname: str,
        appdata: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update application data for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "appname": appname,
            "appdata": appdata,
        }
        return self._make_request("AppdataUpdate", data, request_metadata)

    def request_app_data_update(
        self,
        mode: str,
        identity: str,
        appname: str,
        appdata: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Request update of application data for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "appname": appname,
            "appdata": appdata,
        }
        return self._make_request("AppdataUpdateRequest", data, request_metadata)

    def list_app_data_names(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all application data records for a user."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("AppdataListUserAppNames", data, request_metadata)

    def list_app_names(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all application names in the system."""
        return self._make_request("AppdataListAppNames", None, request_metadata)

    # Legal Basis Management
    def create_legal_basis(
        self, options: Dict[str, Any], request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a legal basis for data processing."""
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
        return self._make_request("LegalBasisCreate", data, request_metadata)

    def update_legal_basis(
        self,
        brief: str,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing legal basis."""
        data = {"brief": brief, **options}
        return self._make_request("LegalBasisUpdate", data, request_metadata)

    def delete_legal_basis(
        self, brief: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete a legal basis."""
        data = {"brief": brief}
        return self._make_request("LegalBasisDelete", data, request_metadata)

    def list_agreements(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all agreements."""
        return self._make_request("LegalBasisListAgreements", None, request_metadata)

    # Agreement Management
    def accept_agreement(
        self,
        mode: str,
        identity: str,
        brief: str,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Accept an agreement for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "brief": brief,
        }
        if options.get("agreementmethod"):
            data["agreementmethod"] = options["agreementmethod"]
        if options.get("lastmodifiedby"):
            data["lastmodifiedby"] = options["lastmodifiedby"]
        if options.get("referencecode"):
            data["referencecode"] = options["referencecode"]
        if options.get("starttime"):
            data["starttime"] = options["starttime"]
        if options.get("finaltime"):
            data["finaltime"] = options["finaltime"]
        if options.get("status"):
            data["status"] = options["status"]
        return self._make_request("AgreementAccept", data, request_metadata)

    def get_user_agreement(
        self,
        mode: str,
        identity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get a specific agreement for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "brief": brief,
        }
        return self._make_request("AgreementGet", data, request_metadata)

    def list_user_agreements(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all agreements for a user."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("AgreementListUserAgreements", data, request_metadata)

    def cancel_agreement(
        self,
        mode: str,
        identity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Cancel an agreement for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "brief": brief,
        }
        return self._make_request("AgreementCancel", data, request_metadata)

    def request_agreement_cancellation(
        self,
        mode: str,
        identity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Request cancellation of an agreement for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "brief": brief,
        }
        return self._make_request("AgreementCancelRequest", data, request_metadata)

    def revoke_all_agreements(
        self, brief: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Revoke all agreements for a specific legal basis."""
        data = {"brief": brief}
        return self._make_request("AgreementRevokeAll", data, request_metadata)

    # Processing Activity Management
    def list_processing_activities(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all processing activities."""
        return self._make_request(
            "ProcessingActivityListActivities", None, request_metadata
        )

    def create_processing_activity(
        self, options: Dict[str, Any], request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new processing activity."""
        data = {
            "activity": options.get("activity"),
            "title": options.get("title"),
            "script": options.get("script"),
            "fulldesc": options.get("fulldesc"),
            "applicableto": options.get("applicableto"),
        }
        return self._make_request("ProcessingActivityCreate", data, request_metadata)

    def update_processing_activity(
        self,
        activity: str,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing processing activity."""
        data = {"activity": activity, **options}
        return self._make_request("ProcessingActivityUpdate", data, request_metadata)

    def delete_processing_activity(
        self, activity: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete a processing activity."""
        data = {"activity": activity}
        return self._make_request("ProcessingActivityDelete", data, request_metadata)

    def link_processing_activity_to_legal_basis(
        self,
        activity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Link a processing activity to a legal basis."""
        data = {
            "activity": activity,
            "brief": brief,
        }
        return self._make_request(
            "ProcessingActivityLinkLegalBasis", data, request_metadata
        )

    def unlink_processing_activity_from_legal_basis(
        self,
        activity: str,
        brief: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Unlink a processing activity from a legal basis."""
        data = {
            "activity": activity,
            "brief": brief,
        }
        return self._make_request(
            "ProcessingActivityUnlinkLegalBasis", data, request_metadata
        )

    # Connector Management
    def list_supported_connectors(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all supported connector types."""
        return self._make_request(
            "ConnectorListSupportedConnectors", None, request_metadata
        )

    def list_connectors(
        self,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List connectors with pagination."""
        data = {"offset": offset, "limit": limit}
        return self._make_request("ConnectorListConnectors", data, request_metadata)

    def create_connector(
        self, options: Dict[str, Any], request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Creates a new database connector with the specified configuration."""
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
        return self._make_request("ConnectorCreate", data, request_metadata)

    def update_connector(
        self,
        connector_ref: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing connector."""
        data = {**options}
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request("ConnectorUpdate", data, request_metadata)

    def validate_connector_connectivity(
        self,
        connector_ref: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate connector connectivity."""
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
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
            data["connectorname"] = options.get("connectorname")
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request(
            "ConnectorValidateConnectivity", data, request_metadata
        )

    def delete_connector(
        self,
        connector_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete a connector."""
        data: Dict[str, Any] = {}
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request("ConnectorDelete", data, request_metadata)

    def get_table_metadata(
        self,
        connector_ref: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get table metadata for a connector."""
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
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
            data["connectorname"] = options.get("connectorname")
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request("ConnectorGetTableMetaData", data, request_metadata)

    def connector_get_user_data(
        self,
        mode: str,
        identity: str,
        connector_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get user data from a connector."""
        data : Dict[str, Any] = {"mode": mode, "identity": identity}
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request("ConnectorGetUserData", data, request_metadata)

    def connector_get_user_extra_data(
        self,
        mode: str,
        identity: str,
        connector_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get user extra data from a connector."""
        data : Dict[str, Any] = {"mode": mode, "identity": identity}
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request("ConnectorGetUserExtraData", data, request_metadata)

    def connector_delete_user(
        self,
        mode: str,
        identity: str,
        connector_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete user data from a connector."""
        data : Dict[str, Any] = {"mode": mode, "identity": identity}
        if isinstance(connector_ref, int) or str(connector_ref).isdigit():
            data["connectorid"] = int(connector_ref)
        else:
            data["connectorname"] = str(connector_ref)
        return self._make_request("ConnectorDeleteUser", data, request_metadata)

    # Group Management
    def create_group(
        self,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new group."""
        data = {
            "groupname": options.get("groupname"),
            "groupdesc": options.get("groupdesc"),
            "grouptype": options.get("grouptype"),
        }
        return self._make_request("GroupCreate", data, request_metadata)

    def get_group(
        self,
        group_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get group information."""
        data : Dict[str, Any] = {}
        if isinstance(group_ref, int) or str(group_ref).isdigit():
            data["groupid"] = int(group_ref)
        else:
            data["groupname"] = str(group_ref)
        return self._make_request("GroupGet", data, request_metadata)

    def list_all_groups(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all groups in the system."""
        return self._make_request("GroupListAllGroups", None, request_metadata)

    def list_user_groups(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List groups for a specific user."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("GroupListUserGroups", data, request_metadata)

    def update_group(
        self,
        group_id: int,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update group information."""
        data = {**options} if options else {}
        data["groupid"] = group_id
        return self._make_request("GroupUpdate", data, request_metadata)

    def delete_group(
        self,
        group_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete a group."""
        data : Dict[str, Any] = {}
        if isinstance(group_ref, int) or str(group_ref).isdigit():
            data["groupid"] = int(group_ref)
        else:
            data["groupname"] = str(group_ref)
        return self._make_request("GroupDelete", data, request_metadata)

    def remove_user_from_group(
        self,
        mode: str,
        identity: str,
        group_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Remove a user from a group."""
        data : Dict[str, Any] = {"mode": mode, "identity": identity}
        if isinstance(group_ref, int) or str(group_ref).isdigit():
            data["groupid"] = int(group_ref)
        else:
            data["groupname"] = str(group_ref)
        return self._make_request("GroupDeleteUser", data, request_metadata)

    def add_user_to_group(
        self,
        mode: str,
        identity: str,
        group_ref: Union[str, int],
        role_ref: Optional[Union[str, int]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a user to a group with an optional role."""
        data: Dict[str, Any] = {"mode": mode, "identity": identity}
        if isinstance(group_ref, int) or str(group_ref).isdigit():
            data["groupid"] = int(group_ref)
        else:
            data["groupname"] = str(group_ref)
        if role_ref is not None:
            if isinstance(role_ref, int) or str(role_ref).isdigit():
                data["roleid"] = int(role_ref)
            else:
                data["rolename"] = str(role_ref)
        return self._make_request("GroupAddUser", data, request_metadata)

    # Token Management
    def create_token(
        self,
        token_type: str,
        record: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a token for sensitive data."""
        data = {"tokentype": token_type, "record": record}
        if options:
            data.update(options)
        return self._make_request("TokenCreate", data, request_metadata)

    def create_tokens_bulk(
        self,
        records: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create multiple tokens in bulk."""
        data = {"records": records}
        if options:
            data.update(options)
        return self._make_request("TokenCreateBulk", data, request_metadata)

    def get_token(
        self, token: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get token information from DatabunkerPro."""
        return self._make_request("TokenGet", {"token": token}, request_metadata)

    def delete_token(
        self, token: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete a token from DatabunkerPro."""
        return self._make_request("TokenDelete", {"token": token}, request_metadata)

    # Audit Management
    def list_user_audit_events(
        self,
        mode: str,
        identity: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List audit events for a specific user."""
        data = {
            "mode": mode,
            "identity": identity,
            "offset": offset,
            "limit": limit,
        }
        return self._make_request("AuditListUserEvents", data, request_metadata)

    def get_audit_event(
        self, audit_event_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a specific audit event by UUID."""
        return self._make_request(
            "AuditGetEvent", {"auditeventuuid": audit_event_uuid}, request_metadata
        )

    # Tenant Management
    def create_tenant(
        self, options: Dict[str, Any], request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new tenant."""
        data = {
            "tenantname": options.get("tenantname"),
            "tenantorg": options.get("tenantorg"),
            "email": options.get("email"),
        }
        return self._make_request("TenantCreate", data, request_metadata)

    def get_tenant(
        self,
        tenant_id: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get tenant information."""
        return self._make_request(
            "TenantGet", {"tenantid": tenant_id}, request_metadata
        )

    def update_tenant(
        self,
        tenant_id: Union[str, int],
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update tenant information."""
        data = {"tenantid": tenant_id, **options}
        return self._make_request("TenantUpdate", data, request_metadata)

    def delete_tenant(
        self,
        tenant_id: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete a tenant."""
        data = {"tenantid": tenant_id}
        return self._make_request("TenantDelete", data, request_metadata)

    def list_tenants(
        self,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all tenants with pagination."""
        data = {
            "offset": offset,
            "limit": limit,
        }
        return self._make_request("TenantListTenants", data, request_metadata)

    # Role Management
    def create_role(
        self,
        options: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new role."""
        data = {
            "rolename": options.get("rolename"),
            "roledesc": options.get("roledesc"),
        }
        return self._make_request("RoleCreate", data, request_metadata)

    def update_role(
        self,
        role_id: Union[str, int],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update role information."""
        data = {**options} if options else {}
        if isinstance(role_id, int) or str(role_id).isdigit():
            data["roleid"] = role_id
        else:
            data["rolename"] = str(role_id)
        return self._make_request("RoleUpdate", data, request_metadata)

    def link_policy(
        self,
        role_ref: Union[str, int],
        policy_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Link a policy to a role."""
        data : Dict[str, Any] = {}
        if isinstance(role_ref, int) or str(role_ref).isdigit():
            data["roleid"] = int(role_ref)
        else:
            data["rolename"] = str(role_ref)
        if isinstance(policy_ref, int) or str(policy_ref).isdigit():
            data["policyid"] = int(policy_ref)
        else:
            data["policyname"] = str(policy_ref)
        return self._make_request("RoleLinkPolicy", data, request_metadata)

    # Policy Management
    def create_policy(
        self,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new policy."""
        data = {
            "policyname": options.get("policyname") if options else None,
            "policydesc": options.get("policydesc") if options else None,
            "policy": options.get("policy") if options else None,
        }
        return self._make_request("PolicyCreate", data, request_metadata)

    def update_policy(
        self,
        policy_id: Union[str, int],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update policy information."""
        data = {**options} if options else {}
        if isinstance(policy_id, int) or str(policy_id).isdigit():
            data["policyid"] = int(policy_id)
        else:
            data["policyname"] = str(policy_id)
        return self._make_request("PolicyUpdate", data, request_metadata)

    def get_policy(
        self,
        policy_ref: Union[str, int],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get policy information."""
        data : Dict[str, Any] = {}
        if isinstance(policy_ref, int) or str(policy_ref).isdigit():
            data["policyid"] = int(policy_ref)
        else:
            data["policyname"] = str(policy_ref)
        return self._make_request("PolicyGet", data, request_metadata)

    def list_policies(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all policies with enhanced information."""
        return self._make_request("PolicyListAllPolicies", None, request_metadata)

    # Bulk Operations
    def bulk_list_unlock(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a bulk list unlock operation."""
        return self._make_request("BulkListUnlock", None, request_metadata)

    def bulk_list_users(
        self,
        unlock_uuid: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List users in a bulk operation."""
        data = {
            "unlockuuid": unlock_uuid,
            "offset": offset,
            "limit": limit,
        }
        return self._make_request("BulkListUsers", data, request_metadata)

    def bulk_list_group_users(
        self,
        unlock_uuid: str,
        group_ref: Union[str, int],
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List users in a group for a bulk operation."""
        data: Dict[str, Any] = {
            "unlockuuid": unlock_uuid,
            "offset": offset,
            "limit": limit,
        }
        if isinstance(group_ref, int) or str(group_ref).isdigit():
            data["groupid"] = int(group_ref)
        else:
            data["groupname"] = str(group_ref)
        return self._make_request("BulkListGroupUsers", data, request_metadata)

    def bulk_list_user_requests(
        self,
        unlock_uuid: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List user requests in a bulk operation."""
        data = {
            "unlockuuid": unlock_uuid,
            "offset": offset,
            "limit": limit,
        }
        return self._make_request("BulkListUserRequests", data, request_metadata)

    def bulk_list_audit_events(
        self,
        unlock_uuid: str,
        offset: int = 0,
        limit: int = 10,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List audit events in a bulk operation."""
        data = {
            "unlockuuid": unlock_uuid,
            "offset": offset,
            "limit": limit,
        }
        return self._make_request("BulkListAuditEvents", data, request_metadata)

    def bulk_list_tokens(
        self,
        unlock_uuid: str,
        tokens: List[str],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List tokens in a bulk operation."""
        data = {
            "unlockuuid": unlock_uuid,
            "tokens": tokens,
        }
        return self._make_request("BulkListTokens", data, request_metadata)

    def bulk_delete_tokens(
        self,
        unlock_uuid: str,
        tokens: List[str],
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete tokens in a bulk operation."""
        data = {
            "unlockuuid": unlock_uuid,
            "tokens": tokens,
        }
        return self._make_request("BulkDeleteTokens", data, request_metadata)

    # System Configuration
    def get_ui_conf(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return self._make_request("TenantGetUIConf")

    def get_tenant_conf(self) -> Dict[str, Any]:
        """Get tenant configuration."""
        return self._make_request("TenantGetConf")

    def get_user_html_report(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get HTML report for a user."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("SystemGetUserHTMLReport", data, request_metadata)

    def get_user_report(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get report for a user."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("SystemGetUserReport", data, request_metadata)

    def get_system_stats(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gets system statistics."""
        return self._make_request("SystemGetSystemStats", None, request_metadata)

    def get_system_metrics(
        self, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get system metrics in Prometheus format."""
        try:
            response = requests.get(f"{self.base_url}/metrics")
            metrics_text = response.text
            return self.parse_prometheus_metrics(metrics_text)
        except Exception as e:
            return {"status": "error", "message": f"Error getting metrics: {str(e)}"}

    def parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """Parse Prometheus metrics text into a dictionary."""
        metrics = {}
        lines = metrics_text.split("\n")
        for line in lines:
            if line.startswith("#") or not line.strip():
                continue
            match = re.match(r"^([a-zA-Z0-9_]+)(?:{([^}]+)})?\s+([0-9.]+)$", line)
            if match:
                name, labels, value = match.groups()
                metric_key = f"{name}{{{labels}}}" if labels else name
                metrics[metric_key] = float(value)
        return metrics

    # Session Management
    def upsert_session(
        self,
        session_uuid: str,
        session_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create or update a session (upsert operation)."""
        data = {"sessionuuid": session_uuid, "sessiondata": session_data}
        if options:
            data.update(options)
        return self._make_request("SessionUpsert", data, request_metadata)

    def delete_session(
        self, session_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete a session."""
        return self._make_request(
            "SessionDelete", {"sessionuuid": session_uuid}, request_metadata
        )

    def list_user_sessions(
        self,
        mode: str,
        identity: str,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List sessions for a specific user."""
        data = {
            "mode": mode,
            "identity": identity,
        }
        return self._make_request("SessionListUserSessions", data, request_metadata)

    def get_session(
        self, session_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get session information."""
        data = {"sessionuuid": session_uuid}
        return self._make_request("SessionGet", data, request_metadata)

    # Shared Record Management
    def create_shared_record(
        self,
        mode: str,
        identity: str,
        options: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Creates a shared record for a user."""
        data = {
            "mode": mode,
            "identity": identity,
            "fields": options.get("fields") if options else None,
            "partner": options.get("partner") if options else None,
            "appname": options.get("appname") if options else None,
            "finaltime": options.get("finaltime") if options else None,
        }
        return self._make_request("SharedRecordCreate", data, request_metadata)

    def get_shared_record(
        self, record_uuid: str, request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gets a shared record by its UUID."""
        data = {"recorduuid": record_uuid}
        return self._make_request("SharedRecordGet", data, request_metadata)
