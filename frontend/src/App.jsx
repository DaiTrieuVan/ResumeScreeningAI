import React, { useState } from 'react';
import Navbar from './components/Navbar';
import RecruiterDashboard from './pages/RecruiterDashboard';
import RealJobsPortal from './pages/RealJobsPortal';
import GapAdvisorView from './pages/GapAdvisorView';

export default function App() {
  const [activeTab, setActiveTab] = useState('real-jobs');

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="app-main">
        {activeTab === 'recruiter' && <RecruiterDashboard />}
        {activeTab === 'real-jobs' && <RealJobsPortal />}
        {activeTab === 'gap-advisor' && <GapAdvisorView />}
      </main>
    </div>
  );
}
