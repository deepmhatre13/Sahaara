"""sos caregiver delivery tracking

Adds the fields the SOS fan-out needs:

* ``caregivers.is_active`` / ``whatsapp_enabled`` — controls SOS eligibility
  without deleting the contact or its notification history.
* ``notifications.caregiver_id`` / ``emergency_event_id`` — links every attempt
  to its recipient and to the single emergency event that caused it.
* ``notifications.status`` / ``provider_message_id`` / ``error_message`` —
  records the provider's real answer (queued / sent / failed + Twilio SID +
  sanitised error) instead of collapsing everything into one boolean.

All new columns are nullable or have server defaults, so existing rows are
backfilled in place and no data is dropped.

Revision ID: b7f1c4a92e03
Revises: 9888eb34d095
Create Date: 2026-09-26 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b7f1c4a92e03'
down_revision = '9888eb34d095'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- caregivers: SOS eligibility flags -----------------------------------
    op.add_column(
        'caregivers',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.add_column(
        'caregivers',
        sa.Column('whatsapp_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.add_column(
        'caregivers',
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # --- notifications: delivery tracking ------------------------------------
    op.add_column('notifications', sa.Column('caregiver_id', sa.UUID(), nullable=True))
    op.add_column('notifications', sa.Column('emergency_event_id', sa.UUID(), nullable=True))
    op.add_column(
        'notifications',
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'pending'")),
    )
    op.add_column('notifications', sa.Column('provider_message_id', sa.String(length=64), nullable=True))
    op.add_column('notifications', sa.Column('error_message', sa.String(length=500), nullable=True))

    # Preserve the meaning of existing rows: anything already flagged delivered
    # is treated as "sent" so the Notifications page keeps rendering correctly.
    op.execute("UPDATE notifications SET status = 'sent' WHERE delivered IS TRUE AND status = 'pending'")
    op.execute("UPDATE notifications SET status = 'failed' WHERE delivered IS FALSE AND status = 'pending'")

    op.create_foreign_key(
        'fk_notifications_caregiver_id',
        'notifications',
        'caregivers',
        ['caregiver_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_notifications_emergency_event_id',
        'notifications',
        'emergency_events',
        ['emergency_event_id'],
        ['id'],
        ondelete='SET NULL',
    )
    # The Notifications page always queries "my notifications, newest first",
    # and the SOS response reads back per-event attempts.
    op.create_index('ix_notifications_user_created', 'notifications', ['user_id', 'created_at'])
    op.create_index('ix_notifications_emergency_event_id', 'notifications', ['emergency_event_id'])
    # SOS caregiver lookup is "active caregivers of this elder".
    op.create_index('ix_caregivers_elder_active', 'caregivers', ['elder_id', 'is_active'])


def downgrade() -> None:
    op.drop_index('ix_caregivers_elder_active', table_name='caregivers')
    op.drop_index('ix_notifications_emergency_event_id', table_name='notifications')
    op.drop_index('ix_notifications_user_created', table_name='notifications')

    op.drop_constraint('fk_notifications_emergency_event_id', 'notifications', type_='foreignkey')
    op.drop_constraint('fk_notifications_caregiver_id', 'notifications', type_='foreignkey')

    op.drop_column('notifications', 'error_message')
    op.drop_column('notifications', 'provider_message_id')
    op.drop_column('notifications', 'status')
    op.drop_column('notifications', 'emergency_event_id')
    op.drop_column('notifications', 'caregiver_id')

    op.drop_column('caregivers', 'updated_at')
    op.drop_column('caregivers', 'whatsapp_enabled')
    op.drop_column('caregivers', 'is_active')
