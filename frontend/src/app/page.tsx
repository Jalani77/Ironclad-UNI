'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { studentApi } from '@/lib/api';
import type { Student } from '@/types';

const STORAGE_KEY = 'ironclad_selected_student_id';

export default function HomePage() {
  const router = useRouter();
  const [students, setStudents] = useState<Student[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const all = await studentApi.list();
        setStudents(all);
        const saved = window.localStorage.getItem(STORAGE_KEY);
        const savedId = saved ? Number(saved) : NaN;
        const initial = Number.isFinite(savedId) ? savedId : all[0]?.id ?? null;
        setSelected(initial);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load students. Is the backend running on http://localhost:8000?');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  function continueAsStudent() {
    if (!selected) return;
    window.localStorage.setItem(STORAGE_KEY, String(selected));
    router.push('/dashboard');
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="w-full max-w-lg rounded-xl bg-white p-8 shadow-2xl">
        <h1 className="text-3xl font-extrabold text-gray-900 text-center">Ironclad</h1>
        <p className="mt-2 text-center text-sm text-gray-600">Select a student to view their deterministic degree audit.</p>

        {loading ? (
          <div className="mt-6 text-center text-sm text-gray-600">Loading students…</div>
        ) : error ? (
          <div className="mt-6 rounded-md bg-red-50 p-4 text-sm text-red-800">{error}</div>
        ) : (
          <div className="mt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Student</label>
              <select
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                value={selected ?? ''}
                onChange={(e) => setSelected(Number(e.target.value))}
              >
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.student_id})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={continueAsStudent}
              className="w-full rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              disabled={!selected}
            >
              Continue
            </button>

            <div className="text-xs text-gray-500">
              This is a “no-password” student picker for the MVP (no real authentication).
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
