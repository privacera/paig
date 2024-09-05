from dataclasses import dataclass, field
from typing import List, Optional, Collection

from .response import Response
from .constants import X_USER_ROLE_HEADER, DEFAULT_OWNER_ROLE, DEFAULT_API_URL_PATTERN
from .paig_exception import PAIGException
from .file_utils import FileUtils
import logging
import re

_logger = logging.getLogger(__name__)


@dataclass
class Permission:
    url_endpoint_pattern: str
    is_exclude: bool
    roles: List[str]
    methods: Optional[List[str]] = field(default_factory=list)

    def to_dict(self):
        return {
            "url_endpoint_pattern": self.url_endpoint_pattern,
            "is_exclude": self.is_exclude,
            "roles": self.roles,
            "methods": self.methods
        }

    @staticmethod
    def from_dict(data):
        return Permission(
            url_endpoint_pattern=data.get("url_endpoint_pattern"),
            is_exclude=data.get("isExclude", False),
            roles=data.get("roles", []),
            methods=data.get("method", [])
        )


class RBACManager:
    _instance = None

    def __new__(cls, rbac_enabled: bool,
                rbac_permission_mapping_file_path="rbac_permission_mapping_file_path.json",
                default_url_patterns=None, default_roles=None, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RBACManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, rbac_enabled: bool,
                 rbac_permission_mapping_file_path="rbac_permission_mapping_file_path.json",
                 default_url_patterns=None, default_roles=None):

        if not self._initialized:
            if default_roles is None:
                default_roles = [DEFAULT_OWNER_ROLE]
            if default_url_patterns is None:
                default_url_patterns = [DEFAULT_API_URL_PATTERN]
            self.rbac_enabled = rbac_enabled
            self.rbac_permission_mapping_file_path = rbac_permission_mapping_file_path
            self.default_url_patterns = default_url_patterns
            self.default_roles = default_roles
            self.permission_list = self.load_permissions()
            self._initialized = True

    def load_permissions(self):
        try:
            permission_json = FileUtils.read_json_file(self.rbac_permission_mapping_file_path)
            return [Permission.from_dict(data) for data in permission_json]
        except Exception as e:
            _logger.error("Failed to load the permissions json file: %s", e)
            raise PAIGException("Failed to load the permissions json file")

    def get_roles_with_permission(self, endpoint, method):
        for permission in self.permission_list:
            if re.match(permission.url_endpoint_pattern, endpoint) and (
                    not permission.methods or (method in permission.methods)):
                return [] if permission.is_exclude else permission.roles

        default_endpoint_patterns = self.default_url_patterns
        default_roles = self.default_roles

        for pattern in default_endpoint_patterns:
            if re.match(pattern, endpoint):
                return default_roles

        return []

    @staticmethod
    def get_instance():
        return RBACManager._instance


def check_user_role_permission(path, method, headers):
    is_filter_enabled = RBACManager.get_instance().rbac_enabled
    user_role = None
    if is_filter_enabled:
        try:
            role_for_endpoint = RBACManager.get_instance().get_roles_with_permission(path, method)
            if role_for_endpoint:
                user_role = headers.get(X_USER_ROLE_HEADER)
                if not user_role:
                    _logger.error(f"Header x-user-role not found for request: {path}")
                    return Response(f"Missing 'x-user-role' header in the request: {path}", status_code=400)
                if user_role not in role_for_endpoint:
                    _logger.error(f"User Role with role: {user_role}, is not authorized to access this request: {path}")
                    return Response(
                        f"User Role with role: {user_role}, is not authorized to access this request: {path}",
                        status_code=403)
        except PAIGException as e:
            _logger.error(f"Failed to check permissions for request: {path}. Error: {e}")
            return Response(f"Failed to check permissions for request: {path}", status_code=500)
    return Response(
        f"User Role with role: {user_role}, is authorized/RBAC is disable to access this request: {path}",
        status_code=200)
