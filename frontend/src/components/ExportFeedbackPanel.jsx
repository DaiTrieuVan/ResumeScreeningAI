import React from 'react';
import { Download, FileSpreadsheet } from 'lucide-react';
import { getExportCsvUrl } from '../services/api';

export default function ExportFeedbackPanel({ selectedJobId, candidateCount }) {
  if (!selectedJobId) return null;

  return (
    <div className="glass-panel export-panel" style={{ padding: '16px 20px', marginBottom: '18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <FileSpreadsheet color="var(--accent-emerald)" size={22} />
        <div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700 }}>Xuất dữ liệu ứng viên</h4>
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
          <Download size={16} /> Đã chọn lọc
        </a>

        <a
          href={getExportCsvUrl(selectedJobId, 'REJECTED')}
          download
          className="btn"
          style={{
            textDecoration: 'none',
            background: '#fff0f1',
            border: '1px solid #f0c7cb',
            color: '#b84250'
          }}
          title="Tải về danh sách ứng viên không đạt tiêu chuẩn để xem xét sau"
        >
          <Download size={16} /> Đã loại
        </a>

        <a
          href={getExportCsvUrl(selectedJobId, 'ALL')}
          download
          className="btn btn-secondary"
          style={{ textDecoration: 'none' }}
        >
          <Download size={16} /> Tất cả ứng viên
        </a>
      </div>
    </div>
  );
}
