import { useMemo, useState } from 'react';

import { HttpTutoringApi, type TutoringApi } from './api/client';
import { CatalogPage } from './pages/CatalogPage';
import { StudentDetailPage } from './pages/StudentDetailPage';
import { StudentsPage } from './pages/StudentsPage';

export interface AppProps {
  api?: TutoringApi;
}

type ActiveSection = 'students' | 'catalog';

export function App({ api }: AppProps) {
  const client = useMemo(() => api ?? new HttpTutoringApi(), [api]);
  const [section, setSection] = useState<ActiveSection>('students');
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);

  return (
    <div className="app-shell">
      <header className="top-bar">
        <div className="top-bar__inner">
          <span className="brand">Cuaderno Pedagógico</span>
          <nav aria-label="Navegación principal" className="nav-tabs">
            <button
              type="button"
              className="nav-tab"
              aria-current={section === 'students' ? 'page' : undefined}
              onClick={() => {
                setSection('students');
                setSelectedStudentId(null);
              }}
            >
              Alumnos
            </button>
            <button
              type="button"
              className="nav-tab"
              aria-current={section === 'catalog' ? 'page' : undefined}
              onClick={() => {
                setSection('catalog');
                setSelectedStudentId(null);
              }}
            >
              Catálogo
            </button>
          </nav>
        </div>
      </header>

      <main className="main-content">
        {section === 'catalog' && <CatalogPage api={client} />}
        {section === 'students' && !selectedStudentId && (
          <StudentsPage
            api={client}
            onSelectStudent={(id) => setSelectedStudentId(id)}
          />
        )}
        {section === 'students' && selectedStudentId && (
          <StudentDetailPage
            api={client}
            studentId={selectedStudentId}
            onBack={() => setSelectedStudentId(null)}
            onNavigateToCatalog={() => {
              setSelectedStudentId(null);
              setSection('catalog');
            }}
          />
        )}
      </main>
    </div>
  );
}

export default App;
