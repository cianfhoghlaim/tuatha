import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/mathematics" as never)({
  component: MathematicsRealm,
});

function MathematicsRealm() {
  return <RealmPage subject="mathematics" />;
}