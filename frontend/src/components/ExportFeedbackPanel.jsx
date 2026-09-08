import React from 'react';
import { Download, FileSpreadsheet } from 'lucide-react';
import { getExportCsvUrl } from '../services/api';

export default function ExportFeedbackPanel({ selectedJobId, candidateCount }) {
  if (!selectedJobId) return null;

  return (
    <div className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <FileSpreadsheet color="var(--accent-emerald)" size={22} />
        <div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700 }}>Xuất Danh sách Ứng viên Chọn lọc</h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Tải file CSV tổng hợp thông tin ứng viên kèm điểm số và giải trình phân tích AI
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <a
          href={getExportCsvUrl(selectedJobId, 'SHORTLISTED')}
          download
          className="btn btn-emerald"
          style={{ textDecoration: 'none' }}
          title="Tải về danh sách ứng viên đạt yêu cầu / điểm cao nhất"
        >
          <Download size={16} /> Xuất DS Chọn lọc (CSV)
        </a>

        <a
          href={getExportCsvUrl(selectedJobId, 'REJECTED')}
          download
          className="btn"
          style={{
            textDecoration: 'none',
            background: 'rgba(244, 63, 94, 0.15)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            color: '#f87171'
          }}
          title="Tải về danh sách ứng viên không đạt tiêu chuẩn để xem xét sau"
        >
          <Download size={16} /> Xuất DS Bị loại (CSV)
        </a>

        <a
          href={getExportCsvUrl(selectedJobId, 'ALL')}
          download
          className="btn btn-secondary"
          style={{ textDecoration: 'none' }}
        >
          <Download size={16} /> Xuất Tất cả Ứng viên
        </a>
      </div>
    </div>
  );
}
