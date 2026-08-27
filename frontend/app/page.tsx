import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SESSION_COOKIE, roleHomePath, verifySessionToken } from "@/lib/session";

export default async function RootPage() {
  const token = cookies().get(SESSION_COOKIE)?.value;
  const session = token ? await verifySessionToken(token) : null;

  redirect(session ? roleHomePath(session.role) : "/login");
}
