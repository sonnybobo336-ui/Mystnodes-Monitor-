import { Toaster } from "sonner";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardPage from "@/pages/DashboardPage";

function App() {
    return (
        <div className="App">
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<DashboardPage />} />
                </Routes>
            </BrowserRouter>
            <Toaster
                theme="dark"
                position="top-right"
                toastOptions={{
                    style: {
                        background: "hsl(222 18% 9%)",
                        color: "hsl(210 20% 96%)",
                        border: "1px solid hsl(222 12% 18%)",
                    },
                }}
            />
        </div>
    );
}

export default App;
