import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/computer_science" as never)({
  component: ComputerScienceRealm,
});

function ComputerScienceRealm() {
  return <RealmPage subject="computer_science" />;
}