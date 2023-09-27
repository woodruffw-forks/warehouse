# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Fix up Enums

Revision ID: 70f918653fc6
Revises: 8eee7a6fa93a
Create Date: 2023-09-18 16:46:15.261547
"""

import sqlalchemy as sa

from alembic import op

revision = "70f918653fc6"
down_revision = "8eee7a6fa93a"


def upgrade():
    op.execute("SET statement_timeout = 60000")
    op.execute("SET lock_timeout = 120000")

    # Rename some enums to follow the autogenerated naming conventions
    op.execute("ALTER TYPE accounts_email_failure_types RENAME TO unverifyreasons ")
    op.execute("ALTER TYPE disable_reason RENAME TO disablereason")
    op.execute("ALTER TYPE ses_event_types RENAME TO eventtypes")
    op.execute("ALTER TYPE ses_email_statuses RENAME TO emailstatuses")

    # Create some missing enums that are text values in the database
    sa.Enum("pending", "expired", name="roleinvitationstatus").create(op.get_bind())
    sa.Enum("Owner", "Maintainer", name="teamprojectroletype").create(op.get_bind())
    sa.Enum("Member", name="teamroletype").create(op.get_bind())
    sa.Enum("pending", "expired", name="organizationinvitationstatus").create(
        op.get_bind()
    )
    sa.Enum(
        "Owner", "Billing Manager", "Manager", "Member", name="organizationroletype"
    ).create(op.get_bind())

    # Alter existing columns to use the created enums
    op.alter_column(
        "organization_invitations",
        "invite_status",
        existing_type=sa.TEXT(),
        type_=sa.Enum("pending", "expired", name="organizationinvitationstatus"),
        postgresql_using="invite_status::text::organizationinvitationstatus",
        existing_nullable=False,
    )
    op.alter_column(
        "organization_roles",
        "role_name",
        existing_type=sa.TEXT(),
        type_=sa.Enum(
            "Owner", "Billing Manager", "Manager", "Member", name="organizationroletype"
        ),
        postgresql_using="role_name::text::organizationroletype",
        existing_nullable=False,
    )
    op.alter_column(
        "organizations",
        "orgtype",
        existing_type=sa.TEXT(),
        type_=sa.Enum("Community", "Company", name="organizationtype"),
        existing_comment="What type of organization such as Community or Company",
        postgresql_using="orgtype::text::organizationtype",
        existing_nullable=False,
    )
    op.alter_column(
        "role_invitations",
        "invite_status",
        existing_type=sa.TEXT(),
        type_=sa.Enum("pending", "expired", name="roleinvitationstatus"),
        postgresql_using="invite_status::text::roleinvitationstatus",
        existing_nullable=False,
    )
    op.alter_column(
        "team_project_roles",
        "role_name",
        existing_type=sa.TEXT(),
        type_=sa.Enum("Owner", "Maintainer", name="teamprojectroletype"),
        postgresql_using="role_name::text::teamprojectroletype",
        existing_nullable=False,
    )
    op.alter_column(
        "team_roles",
        "role_name",
        existing_type=sa.TEXT(),
        type_=sa.Enum("Member", name="teamroletype"),
        postgresql_using="role_name::text::teamroletype",
        existing_nullable=False,
    )

    # Remove leftover enums that are no longer used, removed in #13929
    sa.Enum("event_hook", "scheduled", name="malwarechecktypes").drop(op.get_bind())
    sa.Enum("File", "Release", "Project", name="malwarecheckobjecttype").drop(
        op.get_bind()
    )
    sa.Enum(
        "enabled", "evaluation", "disabled", "wiped_out", name="malwarecheckstate"
    ).drop(op.get_bind())
    sa.Enum("threat", "indeterminate", "benign", name="verdictclassification").drop(
        op.get_bind()
    )
    sa.Enum("low", "medium", "high", name="verdictconfidence").drop(op.get_bind())

    # Sync up existing enum values with the database.
    op.sync_enum_values(
        "public",
        "disablereason",
        ["password compromised", "account frozen"],
        [("users", "disabled_for")],
        enum_values_to_rename=[],
    )
    op.sync_enum_values(
        "public",
        "emailstatuses",
        ["Accepted", "Delivered", "Bounced", "Soft Bounced", "Complained"],
        [("ses_emails", "status")],
        enum_values_to_rename=[],
    )


def downgrade():
    op.execute("ALTER TYPE emailstatuses RENAME TO ses_email_statuses")
    op.execute("ALTER TYPE eventtypes RENAME TO ses_event_types")
    op.execute("ALTER TYPE disablereason RENAME TO disable_reason")
    op.execute("ALTER TYPE unverifyreasons RENAME TO accounts_email_failure_types")

    op.sync_enum_values(
        "public",
        "ses_email_statuses",
        ["Accepted", "Delivered", "Soft Bounced", "Bounced", "Complained"],
        [("ses_emails", "status")],
        enum_values_to_rename=[],
    )
    op.sync_enum_values(
        "public",
        "disable_reason",
        ["password compromised"],
        [("users", "disabled_for")],
        enum_values_to_rename=[],
    )
    sa.Enum("low", "medium", "high", name="verdictconfidence").create(op.get_bind())
    sa.Enum("threat", "indeterminate", "benign", name="verdictclassification").create(
        op.get_bind()
    )
    sa.Enum(
        "enabled", "evaluation", "disabled", "wiped_out", name="malwarecheckstate"
    ).create(op.get_bind())
    sa.Enum("File", "Release", "Project", name="malwarecheckobjecttype").create(
        op.get_bind()
    )
    sa.Enum("event_hook", "scheduled", name="malwarechecktypes").create(op.get_bind())
    op.alter_column(
        "team_roles",
        "role_name",
        existing_type=sa.Enum("Member", name="teamroletype"),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "team_project_roles",
        "role_name",
        existing_type=sa.Enum("Owner", "Maintainer", name="teamprojectroletype"),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "role_invitations",
        "invite_status",
        existing_type=sa.Enum("pending", "expired", name="roleinvitationstatus"),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "organizations",
        "orgtype",
        existing_type=sa.Enum("Community", "Company", name="organizationtype"),
        type_=sa.TEXT(),
        existing_comment="What type of organization such as Community or Company",
        existing_nullable=False,
    )
    op.alter_column(
        "organization_roles",
        "role_name",
        existing_type=sa.Enum(
            "Owner", "Billing Manager", "Manager", "Member", name="organizationroletype"
        ),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "organization_invitations",
        "invite_status",
        existing_type=sa.Enum(
            "pending", "expired", name="organizationinvitationstatus"
        ),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    sa.Enum(
        "Owner", "Billing Manager", "Manager", "Member", name="organizationroletype"
    ).drop(op.get_bind())
    sa.Enum("pending", "expired", name="organizationinvitationstatus").drop(
        op.get_bind()
    )
    sa.Enum("Member", name="teamroletype").drop(op.get_bind())
    sa.Enum("Owner", "Maintainer", name="teamprojectroletype").drop(op.get_bind())
    sa.Enum("pending", "expired", name="roleinvitationstatus").drop(op.get_bind())