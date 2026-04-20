import React from 'react';
import { Target, User } from 'lucide-react';
import type { AnalysisRun, ClientRequest } from '../../types';

interface HeaderProps {
  requests: ClientRequest[];
  runs: AnalysisRun[];
  selectedRequestId: number | null;
  onSelectRequest: (requestId: number) => void;
  onOpenCabinet?: () => void;
}

const Header: React.FC<HeaderProps> = ({ requests, runs, selectedRequestId, onSelectRequest, onOpenCabinet }) => {

  const typeLabel = (t: string) =>
    t === 'market_overview' ? 'Обзор рынка' : t === 'competitive_analysis' ? 'Конкурентный анализ' : t || '—';

  const formatDate = (dt: string) => {
    try {
      return new Date(dt).toLocaleString('ru-RU');
    } catch {
      return dt;
    }
  };

  const activeRun = React.useMemo(() => {
    if (!selectedRequestId) return null;
    const list = runs.filter((r) => r.request_id === selectedRequestId);
    return list.sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0] ?? null;
  }, [runs, selectedRequestId]);

  const showRunning = Boolean(activeRun && (activeRun.status === 'pending' || activeRun.status === 'running'));
  const showError = Boolean(activeRun && activeRun.status === 'error');

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 min-w-0">
            <div className="flex items-center space-x-2">
              <Target className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                MarketScope
              </h1>
            </div>
            <span className="text-sm text-gray-500 truncate">
              Анализ конкурентов HoReCa
            </span>
            {(showRunning || showError) && (
              <div className="flex items-center gap-2">
                {showRunning && (
                  <span className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-600" />
                    Идёт анализ{activeRun?.progress ? ` · ${activeRun.progress}` : ''}
                  </span>
                )}
                {showError && (
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
                    Ошибка анализа
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm text-gray-500">Запрос</span>
              <select
                className="min-w-0 flex-1 sm:flex-none sm:min-w-[280px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedRequestId ?? ''}
                onChange={(e) => onSelectRequest(Number(e.target.value))}
                disabled={!requests.length}
              >
                {!requests.length && <option value="">Нет запросов</option>}
                {requests.map((req, idx) => {
                  const displayNumber = idx + 1;
                  const label = `${formatDate(req.created_at)} · #${displayNumber} · ${typeLabel(req.request_type ?? '')}`;
                  return (
                    <option key={req.id} value={req.id}>
                      {label}
                    </option>
                  );
                })}
              </select>
            </div>
            <button
              type="button"
              onClick={() => onOpenCabinet?.()}
              className="flex items-center justify-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Личный кабинет"
            >
              <User className="w-4 h-4" />
              <span>Личный кабинет</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
