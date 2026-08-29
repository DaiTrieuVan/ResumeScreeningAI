import React, { useState, useEffect } from 'react';
import { Search, Sparkles, UploadCloud, FileText, Loader2, Globe, RefreshCw, Bot } from 'lucide-react';
import RealJobCard from '../components/RealJobCard';
import RealJobFilters from '../components/RealJobFilters';

export default function RealJobsPortal() {
  const [cvFile, setCvFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [crawlStatusMsg, setCrawlStatusMsg] = useState('');
  const [matchResults, setMatchResults] = useState([]);
  const [hasScanned, setHasScanned] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('ALL');
  const [minScore, setMinScore] = useState(0);

  // Initial load: fetch un-matched real jobs
  useEffect(() => {
    fetchInitialJobs();
  }, []);

  const fetchInitialJobs = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/real-jobs');
      const data = await res.json();
      setMatchResults(data.map((j) => ({
        real_job: j,
        match_score: 80.0,
        skills_sub_score: 80.0,
        experience_sub_score: 80.0,
        strengths_summary: ["Vị trí đang tuyển dụng trực tiếp"],
        gaps_summary: ["Tải lên CV để xem phân tích AI riêng"],
        match_reasoning: "Tuyển dụng trực tiếp từ cổng TopCV / ITViec."
      })));
    } catch (err) {
      console.error(err);
    }
  };

  const handleCrawlJobs = async () => {
    setCrawling(true);
    setCrawlStatusMsg('');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/real-jobs/crawl?limit=10', {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Cào dữ liệu thất bại');
      const data = await res.json();
      setCrawlStatusMsg(data.message || 'Đã cào việc làm thực tế thành công!');
      await fetchInitialJobs();
    } catch (err) {
      setCrawlStatusMsg('Lỗi cào dữ liệu: ' + err.message);
    } finally {
      setCrawling(false);
    }
  };

  const handleScanJobs = async (e) => {
    e.preventDefault();
    setLoading(true);
    setHasScanned(true);

    try {
      const formData = new FormData();
      if (cvFile) {
        formData.append('file', cvFile);
      }

      const res = await fetch('http://127.0.0.1:8000/api/real-jobs/match', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error('Không thể quét công việc');
      const data = await res.json();
      setMatchResults(data);
    } catch (err) {
      alert('Lỗi quét việc: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredMatches = matchResults.filter((m) => {
    const job = m.real_job;
    const matchesSearch = 
      (job.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.company_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.required_skills || []).some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesLoc = locationFilter === 'ALL' || job.location_tag === locationFilter;
    const matchesScore = m.match_score >= minScore;

    return matchesSearch && matchesLoc && matchesScore;
  });

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1050px', margin: '0 auto' }}>
      
      {/* Hero Header */}
      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', textAlign: 'center' }}>
        <div style={{
          width: '52px', height: '52px', borderRadius: '16px', background: 'var(--accent-gradient)',
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '12px'
        }}>
          <Globe size={28} color="#fff" />
        </div>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Tìm Việc Thật Trực Tiếp từ TopCV & ITViec</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '650px', margin: '8px auto 0' }}>
          Tải CV của bạn lên để Động cơ AI quét toàn bộ công việc IT/Công nghệ đang tuyển dụng thực tế, chấm điểm độ phù hợp (%) và gợi ý vị trí tốt nhất.
        </p>

        {/* Upload & Crawl Control Bar */}
        <form onSubmit={handleScanJobs} style={{ marginTop: '20px', display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="file"
              accept=".pdf"
              id="cv-upload-realjobs"
              onChange={(e) => setCvFile(e.target.files ? e.target.files[0] : null)}
              style={{ display: 'none' }}
            />
            <label
              htmlFor="cv-upload-realjobs"
              className="btn btn-secondary"
              style={{ cursor: 'pointer', padding: '10px 18px', fontSize: '0.9rem' }}
            >
              <UploadCloud size={18} color="var(--accent-cyan)" />
              {cvFile ? cvFile.name : 'Chọn File CV (PDF)'}
            </label>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ padding: '10px 24px', fontSize: '0.9rem' }}>
            {loading ? (
              <>
                <Loader2 size={18} className="spin" /> Đang Phân tích & Quét Việc Thật...
              </>
            ) : (
              <>
                <Sparkles size={18} /> Quét Việc Thật Phù Hợp Với CV
              </>
            )}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleCrawlJobs}
            disabled={crawling}
            style={{ padding: '10px 18px', fontSize: '0.9rem', borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)' }}
          >
            {crawling ? (
              <>
                <Loader2 size={18} className="spin" /> Đang Cào Dữ Liệu...
              </>
            ) : (
              <>
                <Bot size={18} /> Crawl Dữ Liệu Việc Làm Mới (MVP Bot)
              </>
            )}
          </button>
        </form>

        {crawlStatusMsg && (
          <div style={{ marginTop: '12px', padding: '8px 16px', borderRadius: '8px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', fontSize: '0.85rem', display: 'inline-block' }}>
            {crawlStatusMsg}
          </div>
        )}
      </div>

      {/* Filter Bar */}
      <RealJobFilters
        minScore={minScore}
        setMinScore={setMinScore}
        locationFilter={locationFilter}
        setLocationFilter={setLocationFilter}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      {/* Job Results Count */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', padding: '0 4px' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>
          {hasScanned ? 'Công việc Thật Phù hợp nhất với CV của bạn' : 'Danh sách Công việc Thật Mới nhất'} ({filteredMatches.length})
        </h4>
        {hasScanned && <span className="badge badge-shortlisted">Đã quét & Rerank bởi AI</span>}
      </div>

      {/* Job Cards List */}
      {filteredMatches.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Không tìm thấy vị trí tuyển dụng phù hợp với bộ lọc hiện tại.
        </div>
      ) : (
        filteredMatches.map((m, idx) => (
          <RealJobCard key={m.real_job.id || idx} matchData={m} />
        ))
      )}

    </div>
  );
}

