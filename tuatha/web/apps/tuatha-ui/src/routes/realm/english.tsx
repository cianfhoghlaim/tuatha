import { createFileRoute } from "@tanstack/react-router";
import { RealmPage } from "../../components/RealmPage";

export const Route = createFileRoute("/realm/english" as never)({
  component: EnglishRealm,
});

function EnglishRealm() {
  return <RealmPage subject="english" />;
}