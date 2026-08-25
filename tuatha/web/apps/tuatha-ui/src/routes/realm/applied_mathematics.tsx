import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/applied_mathematics" as never)({
  component: AppliedMathematicsRealm,
});

function AppliedMathematicsRealm() {
  return <RealmPage subject="applied_mathematics" />;
}