// import { deleteExpiredSessions } from '@/db/operations';
// import { createDbConnection } from '@/db/utils';
import app from "@/worker/app";
// import type { Environment } from '@/worker/environment';

export default {
  fetch: app.fetch,

  //   async scheduled(
  //     controller: ScheduledController,
  //     env: Environment
  //   ): Promise<void> {
  //     console.log(`Running scheduled job: ${controller.cron}`);
  //     switch (controller.cron) {
  //       case '0 0 * * 7': // Weekly on Sunday at midnight
  //         const db = createDbConnection(env.DATABASE_URL);
  //         await deleteExpiredSessions(db);
  //         break;
  //       default:
  //         console.warn(`Unknown cron job: ${controller.cron}`);
  //     }
  //     console.log(`Completed scheduled job: ${controller.cron}`);
  //   },
};
