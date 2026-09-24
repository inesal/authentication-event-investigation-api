import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "1m",
};

const BASE = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const eventsRes = http.get(`${BASE}/api/v1/events?limit=100`);
  check(eventsRes, { "events 200": (r) => r.status === 200 });

  const topUsersRes = http.get(`${BASE}/api/v1/suspicious/top-users?n=20`);
  check(topUsersRes, { "top-users 200": (r) => r.status === 200 });

  const timelineRes = http.get(
    `${BASE}/api/v1/suspicious/user-timeline?user=demo-user&bucket=hour`
  );
  check(timelineRes, { "timeline 200": (r) => r.status === 200 || r.status === 404 });
  sleep(1);
}
