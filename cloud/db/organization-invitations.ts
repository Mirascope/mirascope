/**
 * @fileoverview Effect-native Organization Invitations service.
 *
 * Provides authenticated CRUD operations for organization invitations with
 * role-based access control. Invitations allow OWNER/ADMIN to invite users
 * via email who may not yet have accounts.
 *
 * ## Role Hierarchy
 *
 * - `OWNER` - Can invite ADMIN or MEMBER
 * - `ADMIN` - Can invite MEMBER only
 * - `MEMBER` - Cannot invite
 *
 * ## Invitation Lifecycle
 *
 * 1. Create: OWNER/ADMIN sends invitation (generates token, sends email)
 * 2. Pending: Invitation awaits acceptance (7-day expiration)
 * 3. Accept: User clicks link, joins organization (public endpoint)
 * 4. Expire: After 7 days, invitation cannot be accepted
 * 5. Revoke: OWNER/ADMIN cancels invitation before acceptance
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create invitation (sends email)
 * const invitation = yield* db.organizations.invitations.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   data: { recipientEmail: "newuser@example.com", role: "MEMBER" },
 * });
 *
 * // List pending invitations
 * const pending = yield* db.organizations.invitations.findAll({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 * });
 *
 * // Get invitation with metadata for resending email
 * yield* db.organizations.invitations.getWithMetadata({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   invitationId: invitation.id,
 * });
 *
 * // Revoke invitation
 * yield* db.organizations.invitations.revoke({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   invitationId: invitation.id,
 * });
 *
 * // Accept invitation (public, no userId required)
 * yield* db.organizations.invitations.accept({
 *   token: "invitation-token",
 *   acceptingUserId: "user-789",
 * });
 * ```
 */

import { eq, and, gt } from "drizzle-orm";
import { Effect } from "effect";

import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { OrganizationMemberships } from "@/db/organization-memberships";
import {
  organizationInvitations,
  organizationMemberships,
  organizations,
  users,
  type OrganizationInvitation,
  type NewOrganizationInvitation,
  type PublicOrganizationInvitation,
  type PublicOrganizationMembership,
  type OrganizationRole,
  type InvitationRole,
} from "@/db/schema";
import { Users } from "@/db/users";
import {
  AlreadyExistsError,
  DatabaseError,
  ImmutableResourceError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
  SubscriptionPastDueError,
} from "@/errors";
import { Payments } from "@/payments";

/**
 * Public fields to select from organization_invitations table.
 * Excludes token for security when returning to clients.
 */
const publicFields = {
  id: organizationInvitations.id,
  organizationId: organizationInvitations.organizationId,
  senderId: organizationInvitations.senderId,
  recipientEmail: organizationInvitations.recipientEmail,
  role: organizationInvitations.role,
  status: organizationInvitations.status,
  expiresAt: organizationInvitations.expiresAt,
  createdAt: organizationInvitations.createdAt,
  updatedAt: organizationInvitations.updatedAt,
  acceptedAt: organizationInvitations.acceptedAt,
  revokedAt: organizationInvitations.revokedAt,
};

/**
 * All fields including token (for internal service use).
 */
const allFields = {
  ...publicFields,
  token: organizationInvitations.token,
};

/**
 * Extended invitation type with metadata needed for email sending.
 * Returned by create() so API layer has everything needed to send email.
 */
export type OrganizationInvitationWithMetadata = OrganizationInvitation & {
  senderName: string | null;
  senderEmail: string;
  organizationName: string;
};

/**
 * Effect-native Organization Invitations service.
 *
 * ## Permission Matrix
 *
 * | Action   | OWNER | ADMIN | MEMBER |
 * |----------|-------|-------|--------|
 * | create   | ✓*    | ✓**   | ✗      |
 * | read     | ✓     | ✓     | ✗      |
 * | resend   | ✓*    | ✓**   | ✗      |
 * | revoke   | ✓*    | ✓**   | ✗      |
 *
 * *OWNER can invite ADMIN or MEMBER
 * **ADMIN can invite MEMBER only
 *
 * ## Security Model
 *
 * - Cannot invite as OWNER (enforced by database constraint)
 * - Cannot invite existing organization members
 * - Cannot create duplicate pending invitation
 * - Tokens are cryptographically secure (UUID)
 * - Invitations expire after 7 days
 * - Accepting user must match invited email
 */
export class OrganizationInvitations extends BaseAuthenticatedEffectService<
  PublicOrganizationInvitation,
  "organizations/:organizationId/invitations/:invitationId",
  Pick<NewOrganizationInvitation, "recipientEmail" | "role">,
  never, // No update operation - invitations are immutable
  OrganizationRole
> {
  /**
   * Role operation matrix matching organization-memberships pattern.
   * Maps user's org role to invitation roles they can create/manage.
   */
  private static readonly CAN_OPERATE_ON: Record<
    OrganizationRole,
    InvitationRole[]
  > = {
    OWNER: ["ADMIN", "MEMBER"],
    ADMIN: ["MEMBER"],
    MEMBER: [],
  };

  /**
   * Constructor with service dependencies.
   */
  constructor(
    private readonly organizationMemberships: OrganizationMemberships,
    private readonly users: Users,
  ) {
    super();
  }

  private canOperateOnRole(
    userRole: OrganizationRole,
    targetRole: InvitationRole,
  ): boolean {
    return OrganizationInvitations.CAN_OPERATE_ON[userRole].includes(
      targetRole,
    );
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "organization invitation";
  }

  protected getPermissionTable(): PermissionTable<OrganizationRole> {
    return {
      create: ["OWNER", "ADMIN"],
      read: ["OWNER", "ADMIN"],
      // Authorization check runs, then fails as immutable
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER", "ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's role in the organization.
   * Delegates to organization memberships service.
   */
  getRole({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    OrganizationRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return this.organizationMemberships.getRole({ userId, organizationId });
  }

  // ---------------------------------------------------------------------------
  // Private Utility Methods
  // ---------------------------------------------------------------------------

  /**
   * Checks if the invitee is already a member of the organization.
   *
   * @returns Effect that succeeds if no membership exists, fails with AlreadyExistsError otherwise
   */
  private checkExistingMembership(
    organizationId: string,
    normalizedEmail: string,
  ): Effect.Effect<void, AlreadyExistsError | DatabaseError, DrizzleORM> {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [existingMembership] = yield* client
        .select({ memberId: organizationMemberships.memberId })
        .from(organizationMemberships)
        .innerJoin(users, eq(organizationMemberships.memberId, users.id))
        .where(
          and(
            eq(users.email, normalizedEmail),
            eq(organizationMemberships.organizationId, organizationId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to check existing membership",
                cause: e,
              }),
          ),
        );

      if (existingMembership) {
        return yield* Effect.fail(
          new AlreadyExistsError({
            message: "User is already a member of this organization",
            resource: this.getResourceName(),
          }),
        );
      }
    });
  }

  /**
   * Checks if a pending invitation already exists for the email.
   *
   * @returns Effect that succeeds if no invitation exists, fails with AlreadyExistsError otherwise
   */
  private checkExistingInvitation(
    organizationId: string,
    normalizedEmail: string,
  ): Effect.Effect<void, AlreadyExistsError | DatabaseError, DrizzleORM> {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [existingInvitation] = yield* client
        .select({ id: organizationInvitations.id })
        .from(organizationInvitations)
        .where(
          and(
            eq(organizationInvitations.organizationId, organizationId),
            eq(organizationInvitations.recipientEmail, normalizedEmail),
            eq(organizationInvitations.status, "pending"),
            gt(organizationInvitations.expiresAt, new Date()),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to check existing invitation",
                cause: e,
              }),
          ),
        );

      if (existingInvitation) {
        return yield* Effect.fail(
          new AlreadyExistsError({
            message: "A pending invitation already exists for this email",
            resource: this.getResourceName(),
          }),
        );
      }
    });
  }

  /**
   * Retrieves metadata needed for the invitation email.
   *
   * @returns Organization name, sender name, and sender email
   */
  private getInvitationMetadata(
    organizationId: string,
    senderId: string,
  ): Effect.Effect<
    {
      organizationName: string;
      senderName: string | null;
      senderEmail: string;
    },
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Fetch organization details
      const [org] = yield* client
        .select({ id: organizations.id, name: organizations.name })
        .from(organizations)
        .where(eq(organizations.id, organizationId))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to fetch organization",
                cause: e,
              }),
          ),
        );

      if (!org) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Organization not found",
            resource: "organization",
          }),
        );
      }

      const sender = yield* this.users.findById({ userId: senderId });

      return {
        organizationName: org.name,
        senderName: sender.name,
        senderEmail: sender.email,
      };
    });
  }

  // ---------------------------------------------------------------------------
  // Invitation Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new invitation.
   *
   * Validates:
   * - User has permission to invite (OWNER/ADMIN)
   * - Target role is allowed for user's role
   * - Invitee is not already a member
   * - No pending invitation exists for this email
   *
   * Generates secure token and stores invitation.
   * Returns full invitation with token and metadata for API layer to send email.
   */
  create({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: Pick<NewOrganizationInvitation, "recipientEmail" | "role">;
  }): Effect.Effect<
    OrganizationInvitationWithMetadata,
    | AlreadyExistsError
    | NotFoundError
    | PermissionDeniedError
    | DatabaseError
    | PlanLimitExceededError
    | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // 1. Authorize and get role
      const userRole = yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        invitationId: "", // Not needed for create
      });

      // 2. Check if user can invite with this role
      if (!this.canOperateOnRole(userRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot invite a member with role ${data.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      // Normalize email to lowercase for case-insensitive matching
      const normalizedEmail = data.recipientEmail.toLowerCase();

      yield* this.checkExistingMembership(organizationId, normalizedEmail);
      yield* this.checkExistingInvitation(organizationId, normalizedEmail);
      // Check seat limit including pending invitations to prevent over-inviting
      yield* this.organizationMemberships.checkSeatLimit({
        organizationId,
        check: "invitation",
      });

      const metadata = yield* this.getInvitationMetadata(
        organizationId,
        userId,
      );

      const token = crypto.randomUUID();

      // Calculate expiration (7 days from now)
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + 7);

      const [invitation] = yield* client
        .insert(organizationInvitations)
        .values({
          organizationId,
          senderId: userId,
          recipientEmail: normalizedEmail,
          role: data.role,
          token,
          expiresAt,
        })
        .returning(allFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to create invitation",
                cause: e,
              }),
          ),
        );

      // Return full invitation with token and metadata for API layer
      return {
        ...(invitation as OrganizationInvitation),
        ...metadata,
      };
    });
  }

  /**
   * Lists all pending invitations for an organization.
   * Only returns non-expired, pending invitations.
   */
  findAll({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicOrganizationInvitation[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        invitationId: "", // Not needed for list
      });

      const results = yield* client
        .select(publicFields)
        .from(organizationInvitations)
        .where(
          and(
            eq(organizationInvitations.organizationId, organizationId),
            eq(organizationInvitations.status, "pending"),
            gt(organizationInvitations.expiresAt, new Date()),
          ),
        )
        .orderBy(organizationInvitations.createdAt)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list invitations",
                cause: e,
              }),
          ),
        );

      return results as PublicOrganizationInvitation[];
    });
  }

  /**
   * Retrieves a specific invitation by ID.
   */
  findById({
    userId,
    organizationId,
    invitationId,
  }: {
    userId: string;
    organizationId: string;
    invitationId: string;
  }): Effect.Effect<
    PublicOrganizationInvitation,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        invitationId,
      });

      const [invitation] = yield* client
        .select(publicFields)
        .from(organizationInvitations)
        .where(
          and(
            eq(organizationInvitations.id, invitationId),
            eq(organizationInvitations.organizationId, organizationId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find invitation",
                cause: e,
              }),
          ),
        );

      if (!invitation) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invitation not found",
            resource: this.getResourceName(),
          }),
        );
      }

      return invitation as PublicOrganizationInvitation;
    });
  }

  /**
   * Invitations are immutable - this operation always fails.
   *
   * This method exists to satisfy the base service interface and maintain
   * proper authorization checks before rejecting the operation.
   */
  update(args: {
    userId: string;
    organizationId: string;
    invitationId: string;
    data: never;
  }): Effect.Effect<
    PublicOrganizationInvitation,
    | NotFoundError
    | PermissionDeniedError
    | ImmutableResourceError
    | AlreadyExistsError
    | DatabaseError,
    DrizzleORM | Payments
  > {
    // Run authorization first, then fail with ImmutableResourceError
    return this.authorize({
      userId: args.userId,
      action: "update",
      organizationId: args.organizationId,
      invitationId: args.invitationId,
    }).pipe(
      Effect.flatMap(() =>
        Effect.fail(
          new ImmutableResourceError({
            message:
              "Invitations cannot be updated. Use revoke to cancel an invitation.",
            resource: this.getResourceName(),
          }),
        ),
      ),
    );
  }

  /**
   * Invitations are immutable - this operation always fails.
   *
   * This method exists to satisfy the base service interface and maintain
   * proper authorization checks before rejecting the operation.
   */
  delete({
    userId,
    organizationId,
    invitationId,
  }: {
    userId: string;
    organizationId: string;
    invitationId: string;
  }): Effect.Effect<
    void,
    | NotFoundError
    | PermissionDeniedError
    | ImmutableResourceError
    | DatabaseError
    | SubscriptionPastDueError
    | StripeError,
    DrizzleORM | Payments
  > {
    // Run authorization first, then fail with ImmutableResourceError
    return this.authorize({
      userId,
      action: "delete",
      organizationId,
      invitationId,
    }).pipe(
      Effect.flatMap(() =>
        Effect.fail(
          new ImmutableResourceError({
            message:
              "Invitations cannot be deleted. Use revoke to cancel an invitation.",
            resource: this.getResourceName(),
          }),
        ),
      ),
    );
  }

  /**
   * Revokes a pending invitation by updating its status.
   * User clicking the invitation link will receive "invitation has been revoked" error.
   * Maintains audit trail of who invited whom and when it was revoked.
   *
   * Uses "delete" permission semantically since revocation is the soft-delete equivalent.
   */
  revoke({
    userId,
    organizationId,
    invitationId,
  }: {
    userId: string;
    organizationId: string;
    invitationId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const userRole = yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        invitationId,
      });

      // Fetch invitation to check role hierarchy
      const [invitation] = yield* client
        .select({ role: organizationInvitations.role })
        .from(organizationInvitations)
        .where(
          and(
            eq(organizationInvitations.id, invitationId),
            eq(organizationInvitations.organizationId, organizationId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to fetch invitation",
                cause: e,
              }),
          ),
        );

      if (!invitation) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invitation not found",
            resource: this.getResourceName(),
          }),
        );
      }

      // Check if user can operate on this role
      if (!this.canOperateOnRole(userRole, invitation.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot revoke invitation for role ${invitation.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      // Revoke invitation by updating status
      yield* client
        .update(organizationInvitations)
        .set({
          status: "revoked",
          revokedAt: new Date(),
          updatedAt: new Date(),
        })
        .where(eq(organizationInvitations.id, invitationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to revoke invitation",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves invitation with metadata for resending email.
   * Returns the invitation regardless of status or expiration,
   * allowing the caller to perform appropriate validation.
   *
   * This method is used by the API layer to get all necessary information
   * to resend the invitation email (including the token).
   */
  getWithMetadata({
    userId,
    organizationId,
    invitationId,
  }: {
    userId: string;
    organizationId: string;
    invitationId: string;
  }): Effect.Effect<
    OrganizationInvitationWithMetadata,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const userRole = yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        invitationId,
      });

      // Fetch invitation with token (no status/expiration filtering)
      const [invitation] = yield* client
        .select(allFields)
        .from(organizationInvitations)
        .where(
          and(
            eq(organizationInvitations.id, invitationId),
            eq(organizationInvitations.organizationId, organizationId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to fetch invitation",
                cause: e,
              }),
          ),
        );

      if (!invitation) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invitation not found",
            resource: this.getResourceName(),
          }),
        );
      }

      // Check if user can operate on this role
      if (!this.canOperateOnRole(userRole, invitation.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot get metadata for invitation with role ${invitation.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      const metadata = yield* this.getInvitationMetadata(
        organizationId,
        invitation.senderId,
      );

      return {
        ...(invitation as OrganizationInvitation),
        ...metadata,
      };
    });
  }

  /**
   * Accepts an invitation (public method, no userId requirement initially).
   *
   * Validates token, checks expiration, verifies email match, and creates
   * organization membership using the OrganizationMemberships service.
   *
   * All operations are wrapped in a transaction to ensure atomicity:
   * if updating the invitation fails, the membership creation is rolled back.
   */
  accept({
    token,
    acceptingUserId,
  }: {
    token: string;
    acceptingUserId: string;
  }): Effect.Effect<
    PublicOrganizationMembership & { organizationId: string },
    | NotFoundError
    | PermissionDeniedError
    | DatabaseError
    | AlreadyExistsError
    | PlanLimitExceededError
    | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Fetch invitation by token (outside transaction for validation)
      const [invitation] = yield* client
        .select({
          id: organizationInvitations.id,
          organizationId: organizationInvitations.organizationId,
          senderId: organizationInvitations.senderId,
          recipientEmail: organizationInvitations.recipientEmail,
          role: organizationInvitations.role,
          status: organizationInvitations.status,
          expiresAt: organizationInvitations.expiresAt,
        })
        .from(organizationInvitations)
        .where(eq(organizationInvitations.token, token))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to fetch invitation",
                cause: e,
              }),
          ),
        );

      if (!invitation) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invitation not found",
            resource: this.getResourceName(),
          }),
        );
      }

      // Check if already accepted or revoked
      if (invitation.status !== "pending") {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Invitation has already been ${invitation.status}`,
            resource: this.getResourceName(),
          }),
        );
      }

      // Check expiration
      if (invitation.expiresAt < new Date()) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Invitation has expired",
            resource: this.getResourceName(),
          }),
        );
      }

      // Verify accepting user email matches invitation using Users service
      const acceptingUser = yield* this.users.findById({
        userId: acceptingUserId,
      });

      if (
        acceptingUser.email.toLowerCase() !==
        invitation.recipientEmail.toLowerCase()
      ) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Email address does not match invitation",
            resource: this.getResourceName(),
          }),
        );
      }

      // Wrap membership creation + invitation update in a transaction
      const membership = yield* client.withTransaction(
        Effect.gen(this, function* () {
          // Use OrganizationMemberships.create to handle membership creation + audit log
          // The sender becomes the "userId" for authorization purposes
          // The create method uses check: "membership" which only counts actual members,
          // so accepting an invitation (converting pending → member) works correctly
          const newMembership = yield* this.organizationMemberships.create({
            userId: invitation.senderId,
            organizationId: invitation.organizationId,
            data: {
              memberId: acceptingUserId,
              role: invitation.role,
            },
          });

          // Update invitation status
          yield* client
            .update(organizationInvitations)
            .set({
              status: "accepted",
              acceptedAt: new Date(),
              updatedAt: new Date(),
            })
            .where(eq(organizationInvitations.id, invitation.id))
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to update invitation status",
                    cause: e,
                  }),
              ),
            );

          // Return membership with organizationId for redirect purposes
          return {
            ...newMembership,
            organizationId: invitation.organizationId,
          };
        }),
      );

      return membership;
    });
  }
}
