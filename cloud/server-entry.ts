import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import clickhouseQueueConsumer from "@/workers/clickhouseQueueConsumer";

const fetch = createStartHandler(defaultStreamHandler);
const queue = clickhouseQueueConsumer.queue.bind(clickhouseQueueConsumer);

export default {
  fetch,
  queue,
};
