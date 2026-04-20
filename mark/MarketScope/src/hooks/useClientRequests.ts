import { useEffect, useMemo, useState } from 'react';
import { supabase } from '../lib/supabase';
import type { AnalysisRun, ClientRequest } from '../types';

function ensureNumber(id: unknown): number {
  if (typeof id === 'number' && !Number.isNaN(id)) return id;
  if (typeof id === 'string') return parseInt(id, 10) || 0;
  return 0;
}

export function useClientRequests() {
  const [requests, setRequests] = useState<ClientRequest[]>([]);
  const [runs, setRuns] = useState<AnalysisRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [{ data: reqs, error: eReqs }, { data: rns, error: eRuns }] = await Promise.all([
          supabase.from('client_requests').select('*').order('created_at', { ascending: false }),
          supabase.from('analysis_runs').select('*').order('created_at', { ascending: false }),
        ]);
        const err = eReqs || eRuns;
        if (err) throw err;
        if (cancelled) return;
        const mappedReqs = (reqs ?? []).map((r: any) => ({ ...r, id: ensureNumber(r.id) })) as ClientRequest[];
        const mappedRuns = (rns ?? []).map((r: any) => ({
          ...r,
          id: ensureNumber(r.id),
          request_id: ensureNumber(r.request_id),
        })) as AnalysisRun[];
        setRequests(mappedReqs);
        setRuns(mappedRuns);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Ошибка загрузки запросов');
          setRequests([]);
          setRuns([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const runsByRequestId = useMemo(() => {
    const map = new Map<number, AnalysisRun[]>();
    runs.forEach((r) => {
      const list = map.get(r.request_id) ?? [];
      list.push(r);
      map.set(r.request_id, list);
    });
    return map;
  }, [runs]);

  const latestRunId = useMemo(() => runs[0]?.id, [runs]);
  const latestRequestId = useMemo(() => requests[0]?.id, [requests]);

  const reload = async (opts?: { silent?: boolean }) => {
    try {
      if (!opts?.silent) setLoading(true);
      setError(null);
      const [{ data: reqs, error: eReqs }, { data: rns, error: eRuns }] = await Promise.all([
        supabase.from('client_requests').select('*').order('created_at', { ascending: false }),
        supabase.from('analysis_runs').select('*').order('created_at', { ascending: false }),
      ]);
      const err = eReqs || eRuns;
      if (err) throw err;
      const mappedReqs = (reqs ?? []).map((r: any) => ({ ...r, id: ensureNumber(r.id) })) as ClientRequest[];
      const mappedRuns = (rns ?? []).map((r: any) => ({
        ...r,
        id: ensureNumber(r.id),
        request_id: ensureNumber(r.request_id),
      })) as AnalysisRun[];
      setRequests(mappedReqs);
      setRuns(mappedRuns);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки запросов');
    } finally {
      if (!opts?.silent) setLoading(false);
    }
  };

  return { requests, runs, runsByRequestId, latestRunId, latestRequestId, loading, error, reload };
}

