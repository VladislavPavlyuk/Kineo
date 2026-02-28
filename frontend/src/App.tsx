import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ListView } from "./components/ListView";
import { DetailView } from "./components/DetailView";
import { MovieForm } from "./components/MovieForm";
import { SessionsTab } from "./components/SessionsTab";
import "./components/Layout.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ListView />} />
          <Route path="movies/new" element={<MovieForm />} />
          <Route path="movies/:id" element={<DetailView />} />
          <Route path="movies/:id/edit" element={<MovieForm />} />
          <Route path="sessions" element={<SessionsTab />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
