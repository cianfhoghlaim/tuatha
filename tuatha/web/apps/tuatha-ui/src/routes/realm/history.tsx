import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/history" as never)({
  component: HistoryRealm,
});

function HistoryRealm() {
  return <RealmPage subject="history" />;
}