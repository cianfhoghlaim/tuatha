import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/chemistry" as never)({
  component: ChemistryRealm,
});

function ChemistryRealm() {
  return <RealmPage subject="chemistry" />;
}