// tuatha.web.apps.app.mmo.main — the canonical entry point for the British Isles MMO app.
import { createRoot } from "react-dom/client";
import { Provider } from "../../tanstack-start/provider";
import { BugRouter } from "./bug-router";
import { RealmCanvas } from "../../components";

const root = document.getElementById("root");
if (!root) throw new Error("root element not found");
createRoot(root).render(
  <Provider>
    <BugRouter>
      <RealmCanvas student_id="self" subject="mathematics"
                   pdf_path="/src/m.pdf" source_page={3} />
    </BugRouter>
  </Provider>
);
