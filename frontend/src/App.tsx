/**
 * CyberSaathi AI — Root application component.
 *
 * T-01 skeleton: renders a placeholder page that confirms the frontend
 * build is working.  Real pages (URL analysis, message analysis, learning,
 * quiz) are built in T-04 and T-05.
 */

export default function App() {
  return (
    <main className="min-h-screen bg-white flex flex-col items-center justify-center p-6">
      <div className="max-w-lg w-full text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">CyberSaathi AI</h1>
        <p className="text-gray-600">
          Cybersecurity awareness for college students and beginner internet users.
        </p>
        <div className="rounded-md border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800">
          <strong>T-01 skeleton.</strong> The analysis interface will be built in T-04.
          Backend endpoints are ready at{' '}
          <code className="font-mono">http://localhost:8000</code>.
        </div>
        <p className="text-xs text-gray-400">
          This tool does not guarantee safety. Always verify through official channels.
        </p>
      </div>
    </main>
  )
}
