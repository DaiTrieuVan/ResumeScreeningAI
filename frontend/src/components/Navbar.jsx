/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { BriefcaseBusiness, UserRoundCheck, Sparkles, Layers3, Search } from 'lucide-react';

const navigation = [
  { id: 'recruiter', label: 'Không gian tuyển dụng', icon: BriefcaseBusiness },
  { id: 'real-jobs', label: 'Khám phá việc làm', icon: Search },
  { id: 'gap-advisor', label: 'Cố vấn nghề nghiệp', icon: UserRoundCheck },
];

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="app-header">
      <div className="app-header__inner">
        <div className="brand" aria-label="ResumeScreening AI">
          <div className="brand__mark" aria-hidden="true">
            <Sparkles size={21} strokeWidth={2.2} />
          </div>
          <div>
            <h1 className="brand__name">ResumeScreening <span>AI</span></h1>
            <p className="brand__tagline">Tuyển đúng người · Tìm đúng việc</p>
          </div>
        </div>

        <nav className="primary-nav" aria-label="Điều hướng chính">
          {navigation.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={`nav-item ${activeTab === id ? 'active' : ''}`}
              aria-current={activeTab === id ? 'page' : undefined}
            >
              <Icon size={17} strokeWidth={1.9} />
              {label}
            </button>
          ))}
        </nav>

        <div className="engine-badge" title="Mô hình AI đang sử dụng">
          <Layers3 size={14} />
          Gemini 1.5 Flash
        </div>
      </div>
    </header>
  );
}
