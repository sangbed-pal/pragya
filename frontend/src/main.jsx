import { createRoot } from "react-dom/client";
import "./index.css";
import Chat from "./pages/Chat.jsx";
import Home from "./pages/Home.jsx";
import App from "./App.jsx";
import { RouterProvider, createBrowserRouter } from "react-router";

const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        children: [
            {
                path: "",
                element: <Home />,
            },

            {
                path: "chat",
                element: <Chat />,
            },
        ]
    }
]);

createRoot(document.getElementById('root')).render(
    <RouterProvider router={router} />
);
