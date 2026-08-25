import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/gaeilge" as never)({
  component: GaeilgeRealm,
});

function GaeilgeRealm() {
  return <RealmPage subject="gaeilge" />;
}