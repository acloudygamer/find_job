import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ToastProvider } from "./components/ui/Toast";
import DashboardPage from "./features/dashboard/DashboardPage";
import ResumeDetailPage from "./features/resume/ResumeDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/resume/:id" element={<ResumeDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}
