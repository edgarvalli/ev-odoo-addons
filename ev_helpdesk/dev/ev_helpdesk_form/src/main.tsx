import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HelpdeskForm } from "./form.tsx";

createRoot(document.getElementById("ev-helpdesk-form")!).render(
  <StrictMode>
    <HelpdeskForm />
  </StrictMode>,
);
