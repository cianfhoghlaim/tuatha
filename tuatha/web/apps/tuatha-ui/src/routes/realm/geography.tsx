import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/geography" as never)({
  component: GeographyRealm,
});

function GeographyRealm() {
  return <RealmPage subject="geography" />;
}