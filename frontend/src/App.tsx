import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import Contacts from './pages/Contacts';
import Dashboard from './pages/Dashboard';
import ImportExport from './pages/ImportExport';

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="contacts" element={<Contacts />} />
        <Route path="favorites" element={<Contacts favoritesOnly />} />
        <Route path="import-export" element={<ImportExport />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

