import { BaseService } from "./base";
import { sessions, type Session, type PublicSession } from "../schema";

export class SessionService extends BaseService<
  Session,
  PublicSession,
  string,
  typeof sessions
> {
  protected getTable() {
    return sessions;
  }

  protected getResourceName() {
    return "session";
  }

  protected getPublicFields() {
    return {
      id: sessions.id,
      expiresAt: sessions.expiresAt,
    };
  }
}
