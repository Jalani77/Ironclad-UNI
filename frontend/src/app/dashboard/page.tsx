'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AuditReport, Student } from '@/types';
import { auditApi, studentApi } from '@/lib/api';

const STORAGE_KEY = 'ironclad_selected_student_id';

export default function DashboardPage() {
  const router = useRouter();
  const [report, setReport] = useState<AuditReport | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAuditReport = async () => {
      try {
        const all = await studentApi.list();
        setStudents(all);
        const saved = localStorage.getItem(STORAGE_KEY);
        const savedId = saved ? Number(saved) : NaN;
        const initialId = Number.isFinite(savedId) ? savedId : all[0]?.id ?? null;
        setSelectedStudentId(initialId);
        if (!initialId) {
          setError('No students found. Run the seed script to generate mock data.');
          return;
        }
        const data = await auditApi.getAuditReport(initialId);
        setReport(data);
      } catch (err: any) {
        const msg =
          err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          'Failed to load audit report';
        setError(String(msg));
      } finally {
        setLoading(false);
      }
    };

    fetchAuditReport();
  }, [router]);

  const handleLogout = () => {
    // Login removed. Keep a "home" button for UX symmetry.
    router.push('/dashboard');
  };

  const handleStudentChange = async (id: number) => {
    setSelectedStudentId(id);
    setLoading(true);
    setError('');
    try {
      localStorage.setItem(STORAGE_KEY, String(id));
      const data = await auditApi.getAuditReport(id);
      setReport(data);
    } catch {
      setError('Failed to load audit report');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      if (!selectedStudentId) {
        alert('No student selected.');
        return;
      }
      const blob = await auditApi.downloadPDF(selectedStudentId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_report_${report?.student.student_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-600">Loading audit report...</div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-2xl rounded-lg bg-white p-6 shadow">
          <div className="text-xl text-red-600">{error || 'Failed to load report'}</div>
          <div className="mt-3 text-sm text-gray-600">
            If you just removed login, make sure the backend is running and the database is seeded.
          </div>
          <button
            className="mt-4 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700"
            onClick={() => router.push('/')}
          >
            Back to student picker
          </button>
        </div>
      </div>
    );
  }

  const statusColors = {
    completed: 'bg-green-100 text-green-800',
    on_track: 'bg-blue-100 text-blue-800',
    at_risk: 'bg-red-100 text-red-800',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Ironclad Degree Auditor</h1>
              <p className="text-sm text-gray-500">{report.student.name} - {report.student.student_id}</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => router.push('/admin')}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Admin Panel
              </button>
              <button
                onClick={handleDownloadPDF}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700"
              >
                Download PDF
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Student selector */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-900">View audit as</h2>
              <p className="text-xs text-gray-500">Login is disabled; select a seeded student.</p>
            </div>
            <select
              className="w-full md:w-[28rem] border border-gray-300 rounded-md px-3 py-2 text-sm"
              value={selectedStudentId ?? ''}
              onChange={(e) => handleStudentChange(Number(e.target.value))}
            >
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.student_id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Overall Progress Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Overall Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Program</p>
              <p className="text-lg font-semibold text-gray-900">{report.program.code}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Credits Completed</p>
              <p className="text-lg font-semibold text-gray-900">
                {report.total_credits_completed} / {report.total_credits_required}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Progress</p>
              <p className="text-lg font-semibold text-gray-900">{report.overall_percentage}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusColors[report.status]}`}>
                {report.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Completion</span>
              <span>{report.overall_percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className={`h-4 rounded-full ${
                  report.status === 'completed' ? 'bg-green-600' :
                  report.status === 'on_track' ? 'bg-blue-600' :
                  'bg-red-600'
                }`}
                style={{ width: `${report.overall_percentage}%` }}
              ></div>
            </div>
          </div>

          {report.graduation_eligible && (
            <div className="mt-4 p-4 bg-green-50 rounded-md">
              <p className="text-sm font-semibold text-green-800">
                Congratulations! You are eligible for graduation.
              </p>
            </div>
          )}
        </div>

        {/* Requirements Section */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">Requirement Details</h2>

          {report.requirements.map((req) => (
            <div key={req.requirement_id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{req.requirement_name}</h3>
                  <p className="text-sm text-gray-500">{req.requirement_type}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  req.is_met ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {req.is_met ? 'MET' : 'IN PROGRESS'}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500">Credits Required</p>
                  <p className="text-sm font-semibold text-gray-900">{req.credits_required}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Credits Completed</p>
                  <p className="text-sm font-semibold text-gray-900">{req.credits_completed}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Percentage</p>
                  <p className="text-sm font-semibold text-gray-900">{req.percentage}%</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${req.is_met ? 'bg-green-500' : 'bg-yellow-500'}`}
                    style={{ width: `${Math.min(req.percentage, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Completed Courses */}
              {req.completed_courses.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Completed Courses:</p>
                  <div className="flex flex-wrap gap-2">
                    {req.completed_courses.map((course) => (
                      <span
                        key={course.id}
                        className="px-3 py-1 bg-green-50 text-green-700 rounded-md text-xs font-medium border border-green-200"
                      >
                        {course.course_code} ({course.credits} credits)
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Courses */}
              {req.missing_courses.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Missing Courses:</p>
                  <div className="flex flex-wrap gap-2">
                    {req.missing_courses.map((course) => (
                      <span
                        key={course.id}
                        className="px-3 py-1 bg-red-50 text-red-700 rounded-md text-xs font-medium border border-red-200"
                      >
                        {course.course_code} - {course.name} ({course.credits} credits)
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
