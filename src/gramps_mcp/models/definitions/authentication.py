# gramps-mcp - AI-Powered Genealogy Research & Management
# Copyright (C) 2025 cabout.me
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Authentication and security models for the Gramps API.

This module contains JWT token models, OIDC configuration, and credential models.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class JWTAccessToken(BaseModel):
    """
    JWT access token response.

    Attributes:
        access_token: The JWT access token string.
    """

    access_token: str = Field(..., description="Access token")


class JWTRefreshToken(BaseModel):
    """
    JWT refresh token.

    Attributes:
        refresh_token: The refresh token string.
    """

    refresh_token: str = Field(..., description="Refresh token")


class JWTAccessTokens(BaseModel):
    """
    JWT access and refresh token pair.

    Attributes:
        access_token: The JWT access token string.
        refresh_token: The JWT refresh token string.
    """

    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class OIDCProvider(BaseModel):
    """
    OIDC provider configuration.

    Attributes:
        id: Provider identifier.
        name: Provider display name.
        login_url: URL to initiate login with this provider.
    """

    id: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Provider display name")
    login_url: str = Field(..., description="URL to initiate login with provider")


class OIDCConfig(BaseModel):
    """
    OIDC (OpenID Connect) configuration.

    Attributes:
        enabled: Whether OIDC authentication is enabled.
        providers: List of available OIDC providers.
        disable_local_auth: Whether local username/password authentication is disabled.
        auto_redirect: Whether to automatically redirect to OIDC when only one provider.
    """

    enabled: bool = Field(..., description="Whether OIDC authentication is enabled")
    providers: Optional[List[OIDCProvider]] = Field(None, description="List of available OIDC providers")
    disable_local_auth: Optional[bool] = Field(None, description="Whether local authentication is disabled")
    auto_redirect: Optional[bool] = Field(None, description="Whether to auto-redirect to OIDC")


class Credentials(BaseModel):
    """
    Username and password credentials.

    Attributes:
        username: The username for authentication.
        password: The password for authentication.
    """

    username: str = Field(..., description="The username for authentication")
    password: str = Field(..., description="The password for authentication")


class PasswordChange(BaseModel):
    """
    Password change request with old and new passwords.

    Attributes:
        old_password: The current/old password.
        new_password: The new password to set.
    """

    old_password: str = Field(..., description="The old password")
    new_password: str = Field(..., description="The new password")
