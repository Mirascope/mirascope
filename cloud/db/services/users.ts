import { BaseService } from "./base";
import { users, type User, type PublicUser } from "../schema/users";

export class UserService extends BaseService<
  User,
  PublicUser,
  string,
  typeof users
> {
  protected getTable() {
    return users;
  }

  protected getResourceName() {
    return "user";
  }

  protected getPublicFields() {
    return {
      id: users.id,
      email: users.email,
      name: users.name,
    };
  }
}
